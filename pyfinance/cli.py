import click

from pyfinance.config import get_ticker_by_name, TICKERS
from pyfinance.graphics import TickerUploader
from pyfinance.rebalance import csv_to_assets, RebalanceAssets
from pyfinance.simulation import PortfolioSimulator


@click.group()
def cli():
    """PyFinance CLI - Personal finance tools."""
    pass


@cli.command()
@click.argument('name')
@click.argument('ticker')
@click.option('--vm-url', default='http://localhost:8428', 
              help='VictoriaMetrics URL')
def upload_ticker(name: str, ticker: str, vm_url: str):
    """Upload a single ticker's historical data to VictoriaMetrics.
    
    NAME: Label for the ticker in VictoriaMetrics
    TICKER: Yahoo Finance ticker symbol
    """
    uploader = TickerUploader(vm_url)
    click.echo(f"Uploading {name} ({ticker})...")
    uploader.upload_ticker(name, ticker)
    click.echo("Done!")


@cli.command()
@click.option('--vm-url', default='http://localhost:8428',
              help='VictoriaMetrics URL')
def upload_all(vm_url: str):
    """Upload all configured tickers to VictoriaMetrics.
    
    Uploads all tickers defined in config.py plus calculates
    and uploads the mymix weighted portfolio.
    """
    uploader = TickerUploader(vm_url)
    uploader.upload_all()


@cli.command()
@click.argument('threshold', type=int)
@click.argument('csv_file', type=click.Path(exists=True))
def rebalance(threshold: int, csv_file: str):
    """Rebalance portfolio based on threshold and CSV file.
    
    THRESHOLD: Percentage threshold to trigger rebalancing (0-100)
    CSV_FILE: Path to CSV file with assets (name,percentage,value)
    """
    assets = csv_to_assets(csv_file)
    rebalance_assets = RebalanceAssets(assets, threeshold=threshold)
    click.echo(rebalance_assets.information())


@cli.command()
@click.argument('inputs_file', type=click.Path(exists=True))
@click.option('--vm-url', default='http://localhost:8428',
              help='VictoriaMetrics URL')
def simulate(inputs_file: str, vm_url: str):
    """Run portfolio simulation based on inputs."""
    simulator = PortfolioSimulator(vm_url)
    simulator.run(inputs_file)


@cli.command()
def list_tickers():
    """List all configured tickers."""
    click.echo("Configured tickers:")
    for t in TICKERS:
        isin_str = f" (ISIN: {t.isin})" if t.isin else ""
        click.echo(f"  {t.name}: {t.yahoo_ticker}{isin_str}")


if __name__ == '__main__':
    cli()