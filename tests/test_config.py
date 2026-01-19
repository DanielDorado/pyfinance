import pytest
from pyfinance.config import (
    TickerConfig,
    TICKERS,
    PORTFOLIO_WEIGHTS,
    get_ticker_by_name,
    get_portfolio_tickers,
)


def test_ticker_config_creation():
    ticker = TickerConfig("test", "TEST.F", "IE12345")
    assert ticker.name == "test"
    assert ticker.yahoo_ticker == "TEST.F"
    assert ticker.isin == "IE12345"


def test_ticker_config_default_isin():
    ticker = TickerConfig("test", "TEST.F")
    assert ticker.isin == ""


def test_tickers_list_has_six_entries():
    assert len(TICKERS) == 6


def test_tickers_names():
    names = [t.name for t in TICKERS]
    assert "naranja90" in names
    assert "arwen" in names
    assert "usa" in names
    assert "euro" in names
    assert "emerging" in names
    assert "japan" in names


def test_portfolio_weights_sum_to_one():
    total = sum(PORTFOLIO_WEIGHTS.values())
    assert total == pytest.approx(1.0)


def test_portfolio_weights_has_four_entries():
    assert len(PORTFOLIO_WEIGHTS) == 4


def test_get_ticker_by_name_found():
    ticker = get_ticker_by_name("usa")
    assert ticker.name == "usa"
    assert ticker.yahoo_ticker == "IE0032126645.IR"
    assert ticker.isin == "IE0032126645"


def test_get_ticker_by_name_not_found():
    with pytest.raises(ValueError, match="Ticker not found"):
        get_ticker_by_name("nonexistent")


def test_get_portfolio_tickers():
    portfolio = get_portfolio_tickers()
    assert len(portfolio) == 4
    names = [t.name for t in portfolio]
    assert "usa" in names
    assert "euro" in names
    assert "emerging" in names
    assert "japan" in names
    assert "naranja90" not in names
    assert "arwen" not in names
