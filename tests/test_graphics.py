import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from pyfinance.graphics import TickerUploader


@pytest.fixture
def uploader():
    return TickerUploader("http://localhost:8428")


@pytest.fixture
def sample_history():
    """Create sample history DataFrame."""
    dates = pd.date_range('2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'High': [101.0, 102.0, 103.0, 104.0, 105.0],
        'Low': [99.0, 100.0, 101.0, 102.0, 103.0],
        'Close': [100.5, 101.5, 102.5, 103.5, 104.5],
        'Volume': [1000, 1100, 1200, 1300, 1400],
    }, index=dates)


def test_uploader_initialization():
    uploader = TickerUploader()
    assert uploader.vm_client.base_url == "http://localhost:8428"


def test_uploader_custom_url():
    uploader = TickerUploader("http://custom:9999")
    assert uploader.vm_client.base_url == "http://custom:9999"


def test_format_csv(uploader, sample_history):
    csv = uploader.format_csv(sample_history)
    lines = csv.strip().split('\n')
    
    # Check header
    assert lines[0] == "Date,Close"
    
    # Check we have 5 data rows
    assert len(lines) == 6  # header + 5 rows
    
    # Check first data row format
    assert "2024-01-01T00:00:00Z" in lines[1]
    assert "100.5" in lines[1] or lines[1].endswith(",100.5")


def test_format_csv_only_includes_date_and_close(uploader, sample_history):
    csv = uploader.format_csv(sample_history)
    
    # Should not contain other columns
    assert "Open" not in csv
    assert "High" not in csv
    assert "Low" not in csv
    assert "Volume" not in csv


@patch('pyfinance.graphics.yf.Ticker')
def test_download_history(mock_ticker_class, uploader, sample_history):
    mock_ticker = Mock()
    mock_ticker.history.return_value = sample_history
    mock_ticker_class.return_value = mock_ticker
    
    result = uploader.download_history("TEST.F")
    
    mock_ticker_class.assert_called_once_with("TEST.F")
    mock_ticker.history.assert_called_once_with(period="max")
    assert len(result) == 5


def test_calculate_mymix_equal_weights(uploader):
    """Test mymix with equal values gives weighted average."""
    dates = pd.date_range('2024-01-01', periods=3, freq='D')
    
    histories = {
        "usa": pd.DataFrame({'Close': [100.0, 100.0, 100.0]}, index=dates),
        "euro": pd.DataFrame({'Close': [100.0, 100.0, 100.0]}, index=dates),
        "emerging": pd.DataFrame({'Close': [100.0, 100.0, 100.0]}, index=dates),
        "japan": pd.DataFrame({'Close': [100.0, 100.0, 100.0]}, index=dates),
    }
    
    result = uploader.calculate_mymix(histories)
    
    # 100 * 0.30 + 100 * 0.30 + 100 * 0.30 + 100 * 0.10 = 100.0
    for val in result['Close']:
        assert val == pytest.approx(100.0)


def test_calculate_mymix_weighted(uploader):
    """Test mymix calculation with different values."""
    dates = pd.date_range('2024-01-01', periods=1, freq='D')
    
    histories = {
        "usa": pd.DataFrame({'Close': [200.0]}, index=dates),       # 200 * 0.30 = 60
        "euro": pd.DataFrame({'Close': [100.0]}, index=dates),      # 100 * 0.30 = 30
        "emerging": pd.DataFrame({'Close': [50.0]}, index=dates),   # 50 * 0.30 = 15
        "japan": pd.DataFrame({'Close': [100.0]}, index=dates),     # 100 * 0.10 = 10
    }
    
    result = uploader.calculate_mymix(histories)
    
    # 60 + 30 + 15 + 10 = 115
    assert result['Close'].iloc[0] == pytest.approx(115.0)


def test_calculate_mymix_common_dates(uploader):
    """Test that mymix only uses common dates."""
    dates1 = pd.date_range('2024-01-01', periods=5, freq='D')
    dates2 = pd.date_range('2024-01-03', periods=5, freq='D')  # Starts 2 days later
    
    histories = {
        "usa": pd.DataFrame({'Close': [100.0] * 5}, index=dates1),
        "euro": pd.DataFrame({'Close': [100.0] * 5}, index=dates1),
        "emerging": pd.DataFrame({'Close': [100.0] * 5}, index=dates2),
        "japan": pd.DataFrame({'Close': [100.0] * 5}, index=dates1),
    }
    
    result = uploader.calculate_mymix(histories)
    
    # Only 3 common dates: Jan 3, 4, 5
    assert len(result) == 3


def test_calculate_mymix_no_common_dates(uploader):
    """Test error when no common dates exist."""
    dates1 = pd.date_range('2024-01-01', periods=2, freq='D')
    dates2 = pd.date_range('2024-02-01', periods=2, freq='D')
    
    histories = {
        "usa": pd.DataFrame({'Close': [100.0] * 2}, index=dates1),
        "euro": pd.DataFrame({'Close': [100.0] * 2}, index=dates1),
        "emerging": pd.DataFrame({'Close': [100.0] * 2}, index=dates2),
        "japan": pd.DataFrame({'Close': [100.0] * 2}, index=dates1),
    }
    
    with pytest.raises(ValueError, match="No common dates"):
        uploader.calculate_mymix(histories)


@patch.object(TickerUploader, 'download_history')
@patch('pyfinance.victoria.requests.post')
def test_upload_ticker(mock_post, mock_download, uploader, sample_history):
    mock_download.return_value = sample_history
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    uploader.upload_ticker("test", "TEST.F")
    
    mock_download.assert_called_once_with("TEST.F")
    # Should call delete_series and upload_csv
    assert mock_post.call_count == 2


@patch.object(TickerUploader, 'download_history')
def test_upload_ticker_empty_data(mock_download, uploader):
    mock_download.return_value = pd.DataFrame()
    
    with pytest.raises(ValueError, match="No data found"):
        uploader.upload_ticker("test", "TEST.F")
