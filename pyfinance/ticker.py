import datetime
import io
from typing import List, Union
import numpy as np
import pandas as pd
import yfinance as yf


class History:
    """ Class to get historical data from Yahoo Finance.

    Args:
        ticker (str): Ticker symbol of the company.
        start (str): Start date of the data.
        end (str): End date of the data.
"""

    def __init__(self, ticker: str="") -> None:
        self.ticker = ticker
        # Lazy load
        self._history = None


    def _load(self):
        ticker = yf.Ticker(self.ticker)
        df_history = ticker.history(period="max")
        df_history['ticker'] = ticker
        self._history = df_history
        self._reindex()

    def _reindex(self):
        self._history.index = self._history.index.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))

    def from_csv(self, content: str) -> None:
        """ Read the data from a CSV str and populate the Ticker object"""
        buffer = io.StringIO(content)
        self._history = pd.read_csv(buffer)
        self.ticker = self._history['ticker'][0]
        

    def to_csv(self) -> str:
        """ Load the Data if not loaded yet and write them to a CSV file"""
        if self._history is None:
            self._load()
        
        buffer = io.StringIO()
        self._history.to_csv(buffer, index=False)
        return buffer.getvalue()
    
    def close_mean_by_weekday(self) -> List[np.float64]:
        """return seven float64 with the mean value for the Close value
        """
        if self._history is None:
            self._load()
        
        return self._history.groupby(self._history.index.weekday)['Close'].mean()
    




