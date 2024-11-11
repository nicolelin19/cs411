import pytest
from unittest.mock import Mock
import requests
from meal_max.utils.random_utils import get_random

RANDOM_NUMBER = 0.77

def test_get_random_success(mocker):
    """Test to check if a valid decimal number is retrieved from the API."""
    # Mock the requests.get call to simulate a successful API response with a valid decimal number
    mock_response = Mock(status_code=200, text=str(RANDOM_NUMBER))
    mocker.patch("requests.get", return_value=mock_response)

    # Call the function and verify the output
    result = get_random()
    assert result == RANDOM_NUMBER, f"Expected {RANDOM_NUMBER}, got {result}"

def test_get_random_invalid_response(mocker):
    """Test to handle invalid responses that cannot be converted to a float."""
    # Mock the requests.get call to return an invalid response
    mock_response = Mock(status_code=200, text="invalid_number")
    mocker.patch("requests.get", return_value=mock_response)

    # Expect ValueError when the response is not a valid float
    with pytest.raises(ValueError, match="Invalid response from random.org: invalid_number"):
        get_random()

def test_get_random_timeout(mocker):
    """Test if the function handles timeout exceptions correctly."""
    # Mock the requests.get call to raise a timeout exception
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    # Expect RuntimeError when a timeout occurs
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()

def test_get_random_request_exception(mocker):
    """Test if the function handles general request exceptions correctly."""
    # Mock the requests.get call to raise a generic request exception
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Network error"))

    # Expect RuntimeError for a general request failure
    with pytest.raises(RuntimeError, match="Request to random.org failed: Network error"):
        get_random()