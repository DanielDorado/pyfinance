import pytest
from pyfinance import ticker as pfticker

def test_ticker_history_from_csv():
    history = pfticker.History()
    history.from_csv("""Date,Open,High,Low,Close,Volume,Dividends,Stock Splits,ticker
2018-07-27T00:00:00Z,10.0,10.0,10.0,10.0,0,0,0,naranja90
2018-07-30T00:00:00Z,10.0,10.0,10.0,10.0,0,0,0,naranja90
2018-07-31T00:00:00Z,10.0,10.0,10.0,10.0,0,0,0,naranja90
2018-08-01T00:00:00Z,9.991689682006836,9.991689682006836,9.991689682006836,9.991689682006836,0,0,0,naranja90
2018-08-02T00:00:00Z,9.973159790039062,9.973159790039062,9.973159790039062,9.973159790039062,0,0,0,naranja90
2018-08-03T00:00:00Z,10.02299976348877,10.02299976348877,10.02299976348877,10.02299976348877,0,0,0,naranja90
2018-08-06T00:00:00Z,10.025099754333496,10.025099754333496,10.025099754333496,10.025099754333496,0,0,0,naranja90
2018-08-07T00:00:00Z,10.063599586486816,10.063599586486816,10.063599586486816,10.063599586486816,0,0,0,naranja90
2018-08-08T00:00:00Z,10.035200119018555,10.035200119018555,10.035200119018555,10.035200119018555,0,0,0,naranja90
""")

    assert history._history is not None
    assert len(history._history) == 9
    assert history.ticker == 'naranja90'
    assert history._history['ticker'][0] == 'naranja90'
    assert history._history['Date'][0] == '2018-07-27T00:00:00Z'
    assert history._history['Close'][0] == 10.0
    assert history._history['ticker'][8] == 'naranja90'
    assert history._history['Date'][8] == '2018-08-08T00:00:00Z'
    assert history._history['Close'][8] == pytest.approx(10.035200119018555)
    
def test_ticker_history_to_csv():
    history = pfticker.History()
    history.from_csv("""Date,Open,High,Low,Close,Volume,Dividends,Stock Splits,ticker
2018-07-31T00:00:00Z,10.0,10.0,10.0,10.0,0,0,0,naranja90
2018-08-01T00:00:00Z,9.991689682006836,9.991689682006836,9.991689682006836,9.991689682006836,0,0,0,naranja90
""")
 
    csv = history.to_csv()
    assert csv == """Date,Open,High,Low,Close,Volume,Dividends,Stock Splits,ticker
2018-07-31T00:00:00Z,10.0,10.0,10.0,10.0,0,0,0,naranja90
2018-08-01T00:00:00Z,9.991689682006836,9.991689682006836,9.991689682006836,9.991689682006836,0,0,0,naranja90
"""


def test_ticker_close_mean_per_week_day():
    """testing that the Close mean per week day is calculated correctly
"""
    history = pfticker.History()
    # 2018-07-31 was Tuesday
    # In Python Monday is 0 and Sunday is 6 
    history.from_csv("""Date,Open,High,Low,Close,Volume,Dividends,Stock Splits,ticker
2018-07-31T00:00:00Z,0,0,0,10.0,0,0,0,naranja90
2018-08-01T00:00:00Z,0,0,0,11.0,0,0,0,naranja90
2018-08-02T00:00:00Z,0,0,0,12.0,0,0,0,naranja90
2018-08-03T00:00:00Z,0,0,0,13.0,0,0,0,naranja90
2018-08-04T00:00:00Z,0,0,0,14.0,0,0,0,naranja90
2018-08-05T00:00:00Z,0,0,0,15.0,0,0,0,naranja90
2018-08-05T00:00:00Z,0,0,0,16.0,0,0,0,naranja90                     
""")

    history.close_mean_by_weekday()


def test_kk():
    history = pfticker.History("0P0001E1ZI.F")
    assert history.ticker == "0P0001E1ZI.F"