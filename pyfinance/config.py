from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TickerConfig:
    """Configuration for a single ticker."""
    name: str
    yahoo_ticker: str
    isin: str = ""


TICKERS: List[TickerConfig] = [
    TickerConfig("naranja90", "0P0001E1ZI.F"),
    TickerConfig("arwen", "0P0000ISQY.F"),
    TickerConfig("usa", "IE0032126645.IR", "IE0032126645"),
    TickerConfig("euro", "IE0007987690.IR", "IE0007987690"),
    TickerConfig("emerging", "0P0001CJGK.F", "IE00BYX5M476"),
    TickerConfig("japan", "IE0007286036.IR", "IE0007286036"),
]

PORTFOLIO_WEIGHTS: Dict[str, float] = {
    "usa": 0.30,
    "euro": 0.30,
    "emerging": 0.30,
    "japan": 0.10,
}


def get_ticker_by_name(name: str) -> TickerConfig:
    """Get ticker configuration by name."""
    for ticker in TICKERS:
        if ticker.name == name:
            return ticker
    raise ValueError(f"Ticker not found: {name}")


def get_portfolio_tickers() -> List[TickerConfig]:
    """Get tickers that are part of the portfolio (mymix)."""
    return [t for t in TICKERS if t.name in PORTFOLIO_WEIGHTS]
