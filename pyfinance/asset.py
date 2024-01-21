import csv
import importlib
from typing import Union, List


class InvestmentAsset:
    def __init__(self, 
                 asset_type: str, 
                 percentage: int, 
                 product: str, 
                 isin: str, 
                 ticker: str, 
                 expenses: float) -> None:
        self.asset_type = asset_type
        self.percentage = percentage
        self.product = product
        self.isin = isin
        self.ticker = ticker
        self.expenses = expenses


# Global variable to store the assets
assets: List[InvestmentAsset] = []


def load_assets() -> None:
    """Reads the asset information from a CSV file and populates the global
    variable `assets` with the information.
    """
    global assets
    with importlib.resources.open_text('pyfinance.resources', 'assets.csv') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            asset = InvestmentAsset(
                row['Asset'],
                float(row['%']),
                row['Product'],
                row['ISIN'],
                row['Ticker'],
                float(row['Expenses'])
            )
            assets.append(asset)
