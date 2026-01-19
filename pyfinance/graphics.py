import datetime
import io
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf

from pyfinance.config import (
    PORTFOLIO_WEIGHTS,
    TICKERS,
    TickerConfig,
    get_portfolio_tickers,
    get_ticker_by_name,
)
from pyfinance.victoria import VictoriaMetricsClient


class TickerUploader:
    """Handles downloading ticker data and uploading to VictoriaMetrics."""

    def __init__(self, vm_url: str = "http://localhost:8428"):
        self.vm_client = VictoriaMetricsClient(vm_url)

    def download_history(self, yahoo_ticker: str) -> pd.DataFrame:
        """Download full historical data from Yahoo Finance.
        
        Args:
            yahoo_ticker: Yahoo Finance ticker symbol
            
        Returns:
            DataFrame with historical data
        """
        stock = yf.Ticker(yahoo_ticker)
        history = stock.history(period="max")
        return history

    def format_csv(self, df: pd.DataFrame) -> str:
        """Format DataFrame to CSV for VictoriaMetrics import.
        
        Only includes Date and Close columns.
        
        Args:
            df: DataFrame with Close column and DatetimeIndex
            
        Returns:
            CSV string with Date,Close format
        """
        output_df = pd.DataFrame({
            'Date': df.index.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'Close': df['Close'].values
        })
        
        buffer = io.StringIO()
        output_df.to_csv(buffer, index=False)
        return buffer.getvalue()

    def upload_ticker(self, name: str, yahoo_ticker: str) -> None:
        """Download and upload a single ticker to VictoriaMetrics.
        
        Args:
            name: Ticker name for labeling in VictoriaMetrics
            yahoo_ticker: Yahoo Finance ticker symbol
        """
        # Download history
        history = self.download_history(yahoo_ticker)
        if history.empty:
            raise ValueError(f"No data found for ticker: {yahoo_ticker}")
        
        # Format CSV
        csv_data = self.format_csv(history)
        
        # Delete existing data and upload new
        self.vm_client.delete_series(name)
        self.vm_client.upload_csv(csv_data, name)

    def upload_ticker_by_name(self, name: str) -> None:
        """Upload ticker by its configured name.
        
        Args:
            name: Configured ticker name (e.g., 'usa', 'naranja90')
        """
        ticker_config = get_ticker_by_name(name)
        self.upload_ticker(name, ticker_config.yahoo_ticker)

    def calculate_mymix(
        self, histories: Dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """Calculate weighted portfolio average.
        
        Args:
            histories: Dict mapping ticker name to its history DataFrame
            
        Returns:
            DataFrame with weighted Close values
        """
        # Get common dates across all portfolios
        all_indices = [h.index for h in histories.values()]
        common_dates = all_indices[0]
        for idx in all_indices[1:]:
            common_dates = common_dates.intersection(idx)
        
        if len(common_dates) == 0:
            raise ValueError("No common dates found across portfolio tickers")
        
        # Calculate weighted average
        weighted_close = pd.Series(0.0, index=common_dates)
        for name, weight in PORTFOLIO_WEIGHTS.items():
            ticker_close = histories[name].loc[common_dates, 'Close']
            weighted_close += ticker_close * weight
        
        result = pd.DataFrame({'Close': weighted_close}, index=common_dates)
        return result

    def upload_mymix(self) -> None:
        """Download portfolio tickers and upload weighted average."""
        histories = {}
        for ticker_config in get_portfolio_tickers():
            history = self.download_history(ticker_config.yahoo_ticker)
            if not history.empty:
                histories[ticker_config.name] = history
        
        if len(histories) != len(PORTFOLIO_WEIGHTS):
            missing = set(PORTFOLIO_WEIGHTS.keys()) - set(histories.keys())
            raise ValueError(f"Missing data for tickers: {missing}")
        
        mymix_df = self.calculate_mymix(histories)
        csv_data = self.format_csv(mymix_df)
        
        self.vm_client.delete_series("mymix")
        self.vm_client.upload_csv(csv_data, "mymix")

    def upload_all(self) -> None:
        """Upload all configured tickers including mymix."""
        # Upload individual tickers
        for ticker_config in TICKERS:
            print(f"Uploading {ticker_config.name}...")
            self.upload_ticker(ticker_config.name, ticker_config.yahoo_ticker)
        
        # Upload mymix
        print("Calculating and uploading mymix...")
        self.upload_mymix()
        
        # Reset cache
        self.vm_client.reset_cache()
        print("Done!")
