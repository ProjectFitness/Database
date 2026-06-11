import httpx
import respx

from thesis_check.sources.crypto import BINANCE_PREMIUM, COINGECKO_MARKETS, FEAR_GREED, fetch_btc

COINGECKO_ROW = [
    {
        "current_price": 67000.0,
        "market_cap": 1.32e12,
        "price_change_percentage_24h": -1.5,
        "price_change_percentage_7d_in_currency": -4.2,
        "price_change_percentage_30d_in_currency": 8.9,
        "ath_change_percentage": -12.3,
    }
]


@respx.mock
def test_fetch_btc_happy_path():
    respx.get(COINGECKO_MARKETS).mock(return_value=httpx.Response(200, json=COINGECKO_ROW))
    respx.get(BINANCE_PREMIUM).mock(
        return_value=httpx.Response(200, json={"lastFundingRate": "0.000100"})
    )
    respx.get(FEAR_GREED).mock(
        return_value=httpx.Response(
            200, json={"data": [{"value": "27", "value_classification": "Fear"}]}
        )
    )

    indicators = {i.name: i for i in fetch_btc()}

    assert indicators["BTC Price"].value == 67000.0
    assert indicators["BTC Price"].extra["change_30d_pct"] == 8.9
    assert indicators["BTC Market Cap"].value == 1320.0  # billions
    funding = indicators["BTC Perp Funding Rate (8h)"]
    assert funding.value == 0.01
    assert funding.extra["annualized_pct"] == 10.9
    assert indicators["Crypto Fear & Greed Index"].value == 27.0


@respx.mock
def test_fetch_btc_fails_soft_when_all_sources_down():
    for url in (COINGECKO_MARKETS, BINANCE_PREMIUM, FEAR_GREED):
        respx.get(url).mock(return_value=httpx.Response(403))

    indicators = fetch_btc()
    assert indicators, "should still return indicator records"
    assert all(not i.ok for i in indicators)
    assert all(i.error for i in indicators)
