"""Local web dashboard for the monitor.  Run:  python -m monitor.dashboard

Opens a control panel in your browser at http://127.0.0.1:8765 showing:
  - live status of every watch (in stock / out / unknown) with last-checked time
  - your restock history by day of week + hour (from events.csv) so the local
    Target vendor pattern shows up as a chart, not a hunch
  - market price trends for your sealed items (from prices.csv)

It only READS the files the monitor writes (status.json, events.csv, prices.csv),
so it's safe to run alongside the monitor — or on its own to browse history.
Stdlib only; no extra installs. Bound to localhost (not exposed to your network).
"""
from __future__ import annotations

import csv
import json
import webbrowser
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST, PORT = "127.0.0.1", 8765

STATUS_FILE = Path("status.json")
EVENTS_CSV = Path("events.csv")
PRICES_CSV = Path("prices.csv")

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _read_status() -> dict:
    try:
        return json.loads(STATUS_FILE.read_text())
    except (OSError, ValueError):
        return {"updated": None, "watches": []}


def _read_events() -> list[dict]:
    try:
        with EVENTS_CSV.open(newline="") as fh:
            return list(csv.DictReader(fh))
    except OSError:
        return []


def _read_prices() -> list[dict]:
    try:
        with PRICES_CSV.open(newline="") as fh:
            return list(csv.DictReader(fh))
    except OSError:
        return []


def _api_data() -> dict:
    status = _read_status()
    events = _read_events()

    # Restocks bucketed by weekday and by hour — the "what day does my store
    # get stocked" question, answered from your own recorded data.
    by_day = {d: 0 for d in DAYS}
    by_hour = {h: 0 for h in range(24)}
    for e in events:
        if e.get("event") == "restock":
            if e.get("day_of_week") in by_day:
                by_day[e["day_of_week"]] += 1
            try:
                by_hour[int(e["hour"])] += 1
            except (KeyError, ValueError):
                pass

    # Price series per product over time.
    prices = _read_prices()
    series: dict[str, list] = defaultdict(list)
    for row in prices:
        mp = row.get("market_price")
        if mp:
            try:
                series[row["product"]].append({"date": row["date"], "price": float(mp)})
            except ValueError:
                pass

    return {
        "status": status,
        "restocks_by_day": by_day,
        "restocks_by_hour": by_hour,
        "recent_events": list(reversed(events))[:25],
        "price_series": series,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # silence per-request console spam
        pass

    def do_GET(self):
        if self.path.startswith("/api/data"):
            body = json.dumps(_api_data()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path in ("/", "/index.html"):
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)


PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Pokemon Monitor</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  :root { color-scheme: dark; }
  body { font-family: system-ui, sans-serif; margin: 0; background:#0f1115; color:#e6e6e6; }
  header { padding:16px 24px; background:#161a22; border-bottom:1px solid #262b36; }
  h1 { margin:0; font-size:18px; } .sub { color:#8a93a3; font-size:13px; margin-top:4px; }
  main { padding:24px; max-width:1100px; margin:0 auto; }
  .grid { display:grid; gap:16px; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); }
  .card { background:#161a22; border:1px solid #262b36; border-radius:10px; padding:14px; }
  .name { font-weight:600; font-size:14px; } .retailer { color:#8a93a3; font-size:12px; text-transform:capitalize; }
  .pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:700; margin-top:8px; }
  .in { background:#10381f; color:#4ade80; } .out { background:#3a1d20; color:#f87171; }
  .unknown { background:#3a3320; color:#fbbf24; }
  .meta { color:#8a93a3; font-size:12px; margin-top:8px; }
  a { color:#7aa2f7; text-decoration:none; }
  section { margin-top:28px; } h2 { font-size:15px; color:#cbd5e1; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  td,th { text-align:left; padding:6px 8px; border-bottom:1px solid #262b36; }
  .charts { display:grid; gap:16px; grid-template-columns:1fr 1fr; }
  @media(max-width:760px){ .charts{ grid-template-columns:1fr; } }
  canvas { background:#161a22; border:1px solid #262b36; border-radius:10px; padding:8px; }
</style></head>
<body>
<header><h1>Pokemon TCG Monitor</h1><div class="sub" id="updated">loading…</div></header>
<main>
  <section><h2>Live status</h2><div class="grid" id="status"></div></section>
  <section><h2>When do restocks happen? (your recorded data)</h2>
    <div class="charts"><canvas id="dayChart" height="160"></canvas><canvas id="hourChart" height="160"></canvas></div>
  </section>
  <section><h2>Sealed price trends</h2><canvas id="priceChart" height="120"></canvas></section>
  <section><h2>Recent events</h2><table id="events"><thead><tr><th>When</th><th>Day</th><th>Retailer</th><th>Product</th><th>Event</th></tr></thead><tbody></tbody></table></section>
</main>
<script>
let dayC, hourC, priceC;
const PALETTE = ['#7aa2f7','#f7768e','#9ece6a','#e0af68','#bb9af7','#7dcfff','#ff9e64'];
function pill(s){ return s==='in_stock'?'<span class="pill in">IN STOCK</span>'
  : s==='out_of_stock'?'<span class="pill out">out</span>'
  : '<span class="pill unknown">unknown</span>'; }
async function refresh(){
  const d = await (await fetch('/api/data')).json();
  document.getElementById('updated').textContent =
    d.status.updated ? ('last check: ' + new Date(d.status.updated).toLocaleString())
                     : 'monitor not running yet (no status.json)';
  document.getElementById('status').innerHTML = (d.status.watches||[]).map(w =>
    `<div class="card"><div class="name">${w.name}</div>
     <div class="retailer">${w.retailer}</div>${pill(w.stock)}
     <div class="meta">${w.detail||''}</div>
     <div class="meta"><a href="${w.url}" target="_blank">open product ↗</a></div></div>`
  ).join('') || '<div class="meta">No watches reporting yet.</div>';

  const days = Object.keys(d.restocks_by_day), dv = Object.values(d.restocks_by_day);
  const hours = Object.keys(d.restocks_by_hour), hv = Object.values(d.restocks_by_hour);
  dayC = upsert(dayC,'dayChart','bar',days,[{label:'restocks',data:dv,backgroundColor:'#7aa2f7'}]);
  hourC = upsert(hourC,'hourChart','bar',hours.map(h=>h+':00'),[{label:'restocks by hour',data:hv,backgroundColor:'#9ece6a'}]);

  const series = d.price_series||{}; const names=Object.keys(series);
  const labels=[...new Set([].concat(...names.map(n=>series[n].map(p=>p.date))))].sort();
  const ds = names.map((n,i)=>({label:n,data:labels.map(l=>{const m=series[n].find(p=>p.date===l);return m?m.price:null;}),
     borderColor:PALETTE[i%PALETTE.length],spanGaps:true,tension:.2}));
  priceC = upsert(priceC,'priceChart','line',labels,ds);

  document.querySelector('#events tbody').innerHTML = (d.recent_events||[]).map(e=>
    `<tr><td>${(e.timestamp||'').replace('T',' ').slice(0,16)}</td><td>${e.day_of_week||''}</td>
     <td>${e.retailer||''}</td><td>${e.product||''}</td>
     <td>${e.event==='restock'?'🟢 restock':'🔴 sellout'}</td></tr>`).join('');
}
function upsert(chart,id,type,labels,datasets){
  if(chart){ chart.data.labels=labels; chart.data.datasets=datasets; chart.update(); return chart; }
  return new Chart(document.getElementById(id),{type,data:{labels,datasets},
    options:{plugins:{legend:{display:type==='line'}},scales:{x:{ticks:{color:'#8a93a3'}},y:{ticks:{color:'#8a93a3'},beginAtZero:true}}}});
}
refresh(); setInterval(refresh, 5000);
</script>
</body></html>"""


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"Dashboard running at {url}  (Ctrl+C to stop)")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")


if __name__ == "__main__":
    main()
