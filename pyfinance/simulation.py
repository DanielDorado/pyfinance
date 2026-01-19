import io
import pandas as pd
from typing import Dict, Optional, List
from pyfinance.config import get_portfolio_tickers, TICKERS, get_ticker_by_name
from pyfinance.graphics import TickerUploader
from pyfinance.victoria import VictoriaMetricsClient

class InputLoader:
    @staticmethod
    def load_inputs(filepath: str) -> pd.Series:
        """Load inputs from CSV file.
        
        Args:
            filepath: Path to CSV file with Date,Quantity columns.
            
        Returns:
            pd.Series with DatetimeIndex and Quantity values.
        """
        df = pd.read_csv(filepath)
        # Assuming format Date,Quantity
        df['Date'] = pd.to_datetime(df['Date'])
        # If dates are not sorted, sort them
        df = df.sort_values('Date')
        # Normalize to midnight to match history
        df['Date'] = df['Date'].dt.normalize().dt.tz_localize(None)
        return df.set_index('Date')['Quantity']

class PortfolioSimulator:
    def __init__(self, vm_url: str = "http://localhost:8428"):
        self.vm_client = VictoriaMetricsClient(vm_url)
        self.uploader = TickerUploader(vm_url)
        
    def simulate_asset(self, asset_name: str, history: pd.DataFrame, inputs: pd.Series) -> pd.DataFrame:
        """Simulate investing inputs into an asset.
        
        Args:
            asset_name: Name of the asset (for logging).
            history: DataFrame with 'Close' column and DatetimeIndex.
            inputs: Series with DatetimeIndex and amount to invest.
            
        Returns:
            DataFrame with 'Date' and 'Close' (Value) columns.
        """
        if history.empty:
            print(f"Warning: No history for {asset_name}")
            return pd.DataFrame()
            
        # Align inputs to history index
        # We want to reindex the inputs to the history dates
        # Inputs on non-trading days should probably be moved to the next trading day
        # But for simplicity, we can use searchsorted or merge_asof if needed.
        # Simpler approach: Reindex inputs to union of indices, then ffill?
        # No, input is a one-time event.
        
        # Merge history and inputs
        df = history[['Close']].copy()
        df['Input'] = 0.0
        
        # Group inputs by date (in case of multiple inputs on same day)
        daily_inputs = inputs.groupby(inputs.index).sum()
        
        # Add inputs to the dataframe
        # We need to handle inputs that fall on weekends/holidays -> move to next valid date
        # Or just join and fillna(0) then iterate?
        
        # Let's combine indices
        combined_idx = df.index.union(daily_inputs.index).sort_values()
        combined_df = df.reindex(combined_idx)
        combined_df['Input'] = 0.0
        combined_df.loc[daily_inputs.index, 'Input'] = daily_inputs.values
        
        # Forward fill Close price (if input is on weekend, use last Friday's close? Or wait for Monday?)
        # If input is on Sunday, we can't buy until Monday. 
        # Ideally, we should shift input to next valid index in history.
        
        # Better approach:
        # 1. Iterate through inputs.
        # 2. Find insertion point in history index.
        # 3. Add shares.
        
        shares = 0.0
        portfolio_value = []
        dates = []
        
        # We only care about dates in history for the output value series
        # But we need to process inputs.
        
        # Let's align inputs to history dates (next valid trading day)
        valid_inputs = pd.Series(0.0, index=history.index)
        
        for date, amount in daily_inputs.items():
            # Find next valid date
            future_dates = history.index[history.index >= date]
            if not future_dates.empty:
                valid_date = future_dates[0]
                valid_inputs[valid_date] += amount
            else:
                print(f"Warning: Input on {date} is after last history date. Ignoring.")
                
        # Now we have aligned inputs
        # Vectorized simulation
        
        # Price at each day
        prices = history['Close']
        
        # Shares bought at each day: Input / Price
        shares_bought = valid_inputs / prices
        
        # Cumulative shares
        cumulative_shares = shares_bought.cumsum()
        
        # Portfolio value = Cumulative Shares * Price
        value = cumulative_shares * prices
        
        return pd.DataFrame({'Close': value}, index=history.index)

    def simulate_inputs_cumulative(self, inputs: pd.Series, dates: pd.DatetimeIndex) -> pd.DataFrame:
        """Create cumulative sum series of inputs aligned to dates."""
        # Align inputs to these dates as well for comparison
        # Actually, for "inputs" line, we just want the cumulative sum of raw cash injected up to that point.
        
        # Create a series covering the whole range
        if dates.empty:
             return pd.DataFrame()
             
        full_range = pd.Series(0.0, index=dates)
        
        # For each date in index, value is sum of inputs with date <= index
        # To do this efficiently:
        # 1. Create series with inputs
        # 2. Reindex to combined union
        # 3. Cumsum
        # 4. Reindex back to target dates
        
        combined_idx = dates.union(inputs.index).sort_values()
        s = pd.Series(0.0, index=combined_idx)
        # Group inputs by date
        daily = inputs.groupby(inputs.index).sum()
        s.loc[daily.index] = daily.values
        
        cumsum = s.cumsum()
        
        # Forward fill to ensure we have values
        # (Though we started with 0 and added, so missing dates are 0 input, but we want cumulative)
        # Wait, s contains ONLY inputs. 
        # If we reindex, we get NaNs for dates not in inputs.
        
        # Correct approach:
        # 1. Series with inputs at their dates.
        # 2. Reindex to union of (inputs.index, dates), filling with 0.
        # 3. Cumsum.
        # 4. Reindex to 'dates', ffilling.
        
        daily = inputs.groupby(inputs.index).sum()
        union_idx = dates.union(daily.index).sort_values()
        
        expanded = daily.reindex(union_idx, fill_value=0.0)
        cumulative = expanded.cumsum()
        
        result = cumulative.reindex(dates, method='ffill')
        
        return pd.DataFrame({'Close': result}, index=dates)

    def run(self, inputs_file: str):
        print("Loading inputs...")
        inputs = InputLoader.load_inputs(inputs_file)
        if inputs.empty:
            print("No inputs found.")
            return

        print("Fetching histories...")
        histories = {}
        # Get individual tickers
        for ticker_config in TICKERS:
            print(f"  Downloading {ticker_config.name}...")
            hist = self.uploader.download_history(ticker_config.yahoo_ticker)
            if not hist.empty:
                histories[ticker_config.name] = hist
        
        # Calculate mymix
        print("  Calculating mymix...")
        try:
            mymix_df = self.uploader.calculate_mymix(histories)
            histories['mymix'] = mymix_df
        except ValueError as e:
            print(f"Error calculating mymix: {e}")

        # Determine common date range for simulation outputs?
        # Or just use each asset's history range?
        # The prompt implies comparing them. It's best if they share the X axis mostly, 
        # but using the asset's own history is fine.
        
        # However, for the 'inputs' baseline, we need a reference date range.
        # We can use the union of all history dates, or just mymix's range.
        # Let's use mymix's range as the "canonical" portfolio range if available, else union.
        
        reference_dates = pd.Index([])
        if 'mymix' in histories:
            reference_dates = histories['mymix'].index
        elif histories:
             reference_dates = list(histories.values())[0].index
             
        # Upload Inputs Baseline
        print("Simulating and uploading Inputs baseline...")
        inputs_value = self.simulate_inputs_cumulative(inputs, reference_dates)
        csv_data = self.uploader.format_csv(inputs_value)
        self.vm_client.delete_series("inputs", metric_name="finance_simulation_value")
        self.vm_client.upload_csv(csv_data, "inputs", metric_name="finance_simulation_value")
        
        # Simulate and Upload Assets
        for name, history in histories.items():
            print(f"Simulating and uploading {name}...")
            sim_value = self.simulate_asset(name, history, inputs)
            csv_data = self.uploader.format_csv(sim_value)
            
            # Using metric name 'finance_simulation_value'
            self.vm_client.delete_series(name, metric_name="finance_simulation_value")
            self.vm_client.upload_csv(csv_data, name, metric_name="finance_simulation_value")
            
        print("Simulation complete.")
        self.vm_client.reset_cache()
