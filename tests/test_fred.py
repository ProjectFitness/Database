import httpx
import respx

from thesis_check.sources.fred import FREDGRAPH_URL, fetch_macro


def _csv(series: str, rows: list[tuple[str, str]]) -> str:
    return "observation_date," + series + "\n" + "\n".join(f"{d},{v}" for d, v in rows)


@respx.mock
def test_fetch_macro_parses_latest_value():
    def responder(request):
        series = request.url.params["id"]
        if series == "CPIAUCSL":
            # 13 monthly observations: 300 -> 309 gives exactly 3.0% YoY
            rows = [(f"2025-{m:02d}-01", str(300 + (m - 1) * 0.75)) for m in range(1, 14)]
            return httpx.Response(200, text=_csv(series, rows))
        return httpx.Response(
            200,
            text=_csv(series, [("2026-06-09", "."), ("2026-06-10", "4.33")]),
        )

    respx.get(FREDGRAPH_URL).mock(side_effect=responder)

    indicators = {i.name: i for i in fetch_macro()}

    fed = indicators["Effective Fed Funds Rate"]
    assert fed.ok
    assert fed.value == 4.33
    assert fed.as_of == "2026-06-10"

    cpi = indicators["CPI Inflation (YoY)"]
    assert cpi.ok
    assert cpi.value == 3.0


@respx.mock
def test_fetch_macro_fails_soft_per_series():
    def responder(request):
        if request.url.params["id"] == "DFF":
            return httpx.Response(403)
        return httpx.Response(200, text=_csv("X", [("2026-06-10", "1.0")] * 13))

    respx.get(FREDGRAPH_URL).mock(side_effect=responder)

    indicators = {i.name: i for i in fetch_macro()}
    assert not indicators["Effective Fed Funds Rate"].ok
    assert indicators["Effective Fed Funds Rate"].error
    assert indicators["10-Year Treasury Yield"].ok
