import pytest
import httpx
from unittest.mock import MagicMock, patch
from web.app.api_client import _handle_response, APIError

def test_handle_response_401():
    response = MagicMock(spec=httpx.Response)
    response.status_code = 401

    with patch("web.app.api_client.session") as mock_session, \
         patch("web.app.api_client.flash") as mock_flash:
        with pytest.raises(APIError) as excinfo:
            _handle_response(response)

        assert excinfo.value.status_code == 401
        assert excinfo.value.detail == "session_expired"
        mock_session.clear.assert_called_once()
        mock_flash.assert_called_once_with("Session expired. Please log in again.", "error")


def test_handle_response_204():
    response = MagicMock(spec=httpx.Response)
    response.status_code = 204

    result = _handle_response(response)

    assert result is None
    response.raise_for_status.assert_called_once()


def test_handle_response_200():
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    expected_data = {"key": "value"}
    response.json.return_value = expected_data

    result = _handle_response(response)

    assert result == expected_data
    response.raise_for_status.assert_called_once()
    response.json.assert_called_once()


def test_handle_response_error():
    response = MagicMock(spec=httpx.Response)
    response.status_code = 500
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Internal Server Error", request=MagicMock(), response=response
    )

    with pytest.raises(httpx.HTTPStatusError):
        _handle_response(response)

    response.raise_for_status.assert_called_once()
