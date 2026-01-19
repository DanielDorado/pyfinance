import pytest
from unittest.mock import Mock, patch
from pyfinance.victoria import VictoriaMetricsClient


@pytest.fixture
def client():
    return VictoriaMetricsClient("http://localhost:8428")


def test_client_initialization():
    client = VictoriaMetricsClient()
    assert client.base_url == "http://localhost:8428"


def test_client_custom_url():
    client = VictoriaMetricsClient("http://custom:9999")
    assert client.base_url == "http://custom:9999"


@patch('pyfinance.victoria.requests.post')
def test_upload_csv(mock_post, client):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    csv_data = "Date,Close\n2024-01-01T00:00:00Z,100.0\n"
    client.upload_csv(csv_data, "test_ticker")

    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "http://localhost:8428/api/v1/import/csv"
    assert call_args[1]["data"] == csv_data
    assert "format" in call_args[1]["params"]
    assert call_args[1]["params"]["extra_label"] == "ticker=test_ticker"


@patch('pyfinance.victoria.requests.get')
def test_reset_cache(mock_get, client):
    client.reset_cache()
    mock_get.assert_called_once_with(
        "http://localhost:8428/internal/resetRollupResultCache"
    )


@patch('pyfinance.victoria.requests.post')
def test_delete_series(mock_post, client):
    client.delete_series("test_ticker")
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[0][0] == "http://localhost:8428/api/v1/admin/tsdb/delete_series"
    assert 'ticker="test_ticker"' in call_args[1]["params"]["match[]"]


@patch('pyfinance.victoria.requests.get')
def test_health_check_success(mock_get, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    assert client.health_check() is True
    mock_get.assert_called_once_with("http://localhost:8428/health")


@patch('pyfinance.victoria.requests.get')
def test_health_check_failure(mock_get, client):
    import requests as req
    mock_get.side_effect = req.exceptions.ConnectionError()

    assert client.health_check() is False
