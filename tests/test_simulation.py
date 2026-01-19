import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from pyfinance.simulation import InputLoader, PortfolioSimulator

@pytest.fixture
def sample_inputs_csv(tmp_path):
    p = tmp_path / "inputs.csv"
    p.write_text("Date,Quantity\n2024-01-01,1000\n2024-02-01,500\n")
    return str(p)

def test_input_loader(sample_inputs_csv):
    inputs = InputLoader.load_inputs(sample_inputs_csv)
    assert len(inputs) == 2
    assert inputs.index[0] == pd.Timestamp('2024-01-01')
    assert inputs.iloc[0] == 1000
    assert inputs.iloc[1] == 500

def test_simulate_asset_logic():
    # Setup history: Price stays at 100
    dates = pd.date_range('2024-01-01', periods=60, freq='D')
    history = pd.DataFrame({'Close': [100.0] * 60}, index=dates)
    
    # Inputs: 1000 on Jan 1, 500 on Jan 10
    inputs_idx = pd.DatetimeIndex([pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-10')])
    inputs = pd.Series([1000.0, 500.0], index=inputs_idx)
    
    sim = PortfolioSimulator()
    result = sim.simulate_asset("test", history, inputs)
    
    # Check value at start: 1000 invested / 100 price = 10 shares. Value = 10 * 100 = 1000.
    assert result.loc['2024-01-01', 'Close'] == 1000.0
    
    # Check value at Jan 5 (before second input): Still 1000
    assert result.loc['2024-01-05', 'Close'] == 1000.0
    
    # Check value at Jan 10: +500 invested / 100 price = +5 shares. Total 15 shares. Value = 1500.
    assert result.loc['2024-01-10', 'Close'] == 1500.0
    
    # Check end
    assert result.iloc[-1]['Close'] == 1500.0

def test_simulate_asset_price_change():
    # Setup history: Price doubles from 100 to 200
    dates = pd.date_range('2024-01-01', periods=2, freq='D')
    history = pd.DataFrame({'Close': [100.0, 200.0]}, index=dates)
    
    inputs = pd.Series([1000.0], index=pd.DatetimeIndex([pd.Timestamp('2024-01-01')]))
    
    sim = PortfolioSimulator()
    result = sim.simulate_asset("test", history, inputs)
    
    # Day 1: Buy 10 shares (1000/100). Value 1000.
    assert result.iloc[0]['Close'] == 1000.0
    
    # Day 2: 10 shares * 200 price = 2000.
    assert result.iloc[1]['Close'] == 2000.0

def test_simulate_inputs_cumulative():
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    inputs_idx = pd.DatetimeIndex([pd.Timestamp('2024-01-01'), pd.Timestamp('2024-01-03')])
    inputs = pd.Series([1000.0, 500.0], index=inputs_idx)
    
    sim = PortfolioSimulator()
    result = sim.simulate_inputs_cumulative(inputs, dates)
    
    # Jan 1: 1000
    assert result.loc['2024-01-01', 'Close'] == 1000.0
    # Jan 2: 1000
    assert result.loc['2024-01-02', 'Close'] == 1000.0
    # Jan 3: 1500
    assert result.loc['2024-01-03', 'Close'] == 1500.0
    # Jan 5: 1500
    assert result.loc['2024-01-05', 'Close'] == 1500.0
