import requests
from typing import Optional


class VictoriaMetricsClient:
    """Client for uploading data to VictoriaMetrics."""

    def __init__(self, base_url: str = "http://localhost:8428"):
        self.base_url = base_url

    def upload_csv(self, csv_data: str, name: str, metric_name: str = "finance_close") -> None:
        """Upload CSV data with ticker label.
        
        Args:
            csv_data: CSV string with Date,Close columns
            name: Ticker name for labeling
            metric_name: Name of the metric (default: finance_close)
        """
        format_str = f"1:time:rfc3339,2:metric:{metric_name}"
        url = f"{self.base_url}/api/v1/import/csv"
        params = {
            "format": format_str,
            "extra_label": f"ticker={name}"
        }
        response = requests.post(url, data=csv_data, params=params)
        response.raise_for_status()

    def reset_cache(self) -> None:
        """Reset rollup result cache."""
        url = f"{self.base_url}/internal/resetRollupResultCache"
        requests.get(url)

    def delete_series(self, name: str, metric_name: str = "finance_close") -> None:
        """Delete existing series for a ticker (for full replacement)."""
        url = f"{self.base_url}/api/v1/admin/tsdb/delete_series"
        params = {"match[]": f'{metric_name}{{ticker="{name}"}}'}
        requests.post(url, params=params)

    def health_check(self) -> bool:
        """Check if VictoriaMetrics is reachable."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
