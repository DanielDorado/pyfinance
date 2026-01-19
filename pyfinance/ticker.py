import datetime
import io
import sys
from typing import List
import numpy as np
import pandas as pd
import yfinance as yf
from collections import namedtuple
import calendar


_TICKER = {
    "naranja90": "0P0001E1ZI.F", # Fondo Común de Inversión Naranja 90 comparado con MSCI World net total return eur index
    "arwen": "0P0000ISQY.F",  # SICAV Arwen
    "us": "IE0032126645", # Vanguard U.S. 500 Stock Index Fund EUR Acc
    "eur": "IE0007987690", # VANGUARD EUROPEAN STOCK EU INV
    "emerging": "IE00BYX5M476", #  Fidelity MSCI Emerging Markets Index Fund P-ACC-EUR
    "japan": "IE0007286036", # Vanguard Japan Stock Index Fund EUR Acc
    "world": "IE00BYX5NX33", # Fidelity MSCI World Index Fund P-ACC-EUR
}
 
TICKER = namedtuple('Struct', _TICKER.keys())(*_TICKER.values()) 

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
        self._stock: yf.Ticker = None
        self._history: pd.core.frame.DataFrame = None


    def _load(self):
        self.stock = yf.Ticker(self.ticker)
        df_history = self.stock.history(period="max")
        df_history['ticker'] = self.stock
        self._history = df_history
        self._reindex()

    def _reindex(self):
        # self._history.index = self._history.index.map(lambda x: datetime.datetime.strftime(x, '%Y-%m-%dT%H:%M:%SZ'))
        self._history.index = pd.to_datetime(self._history.index)

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
    

def get_dataframe_by_weekday(df: pd.core.frame.DataFrame, week_day: int) -> pd.core.frame.DataFrame:
    dfwd = df[df.index.dayofweek == week_day]
    if (len(dfwd) == 0):
        #  put the day name of the week in the error message
        print(f"No data for {calendar.day_name[week_day]}")
        return None
    print(f"First day {dfwd.iloc[0].name.day_name()}")
    print(f"Last day {dfwd.iloc[-1].name.day_name()}")
    print(f"Length {len(dfwd)}")
    return dfwd


def explore(ticker: str):
    history = History(ticker)
    history._load()
    h = history._history
    print(h.head())
    print(h.tail())
    return history


if __name__ == '__main__':
    history = History(sys.argv[1])
    print(history.close_mean_by_weekday())
    print(history.to_csv())
    history.from_csv(history.to_csv())
    print(history.close_mean_by_weekday())
    print(history.to_csv)
