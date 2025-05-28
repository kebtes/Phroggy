import pytest
from unittest.mock import patch, AsyncMock, ANY
from aiohttp import ClientError

from services.check_url import check_url, send_url_for_check, extract_threat_types
# from ser.check_url import check_url, send_url_for_check, extract_threat_types


@pytest.mark.asyncio
# Test that extract_threat_types correctly extracts threat types from a response
# containing matches with threat entries.
async def test_extract_threat_types_with_matches():
    response_data = {
        "matches": [
            {"threatType": "MALWARE"},
            {"threatType": "SOCIAL_ENGINEERING"},
        ]
    }
    result = await extract_threat_types(response_data)
    assert result == ["MALWARE", "SOCIAL_ENGINEERING"]


@pytest.mark.asyncio
# Test that extract_threat_types returns an empty list when the response
# data does not contain any matches.
async def test_extract_threat_types_no_matches():
    response_data = {}
    result = await extract_threat_types(response_data)
    assert result == []

@pytest.mark.asyncio
@patch("services.check_url.extract_links", new_callable=AsyncMock)
@patch("services.check_url.send_url_for_check", new_callable=AsyncMock)
@patch("services.check_url.extract_threat_types", new_callable=AsyncMock)
# Test that check_url returns (False, {}) immediately if no links are extracted from the input text.
# Ensures no further calls to network or threat extraction are made.
async def test_check_url_no_links(mock_extract_threat_types, mock_send_url_for_check, mock_extract_links):
    mock_extract_links.return_value = []
    result = await check_url("some text")
    assert result == (False, {})
    mock_extract_links.assert_awaited_once()
    mock_send_url_for_check.assert_not_called()
    mock_extract_threat_types.assert_not_called()


@pytest.mark.asyncio
@patch("services.check_url.extract_links", new_callable=AsyncMock)
@patch("services.check_url.send_url_for_check", new_callable=AsyncMock)
@patch("services.check_url.extract_threat_types", new_callable=AsyncMock)
# Test that check_url returns correct threat report and True if at least one threat is found.
# Mocks two URLs where one returns a threat and the other does not.
async def test_check_url_with_threats(mock_extract_threat_types, mock_send_url_for_check, mock_extract_links):
    mock_extract_links.return_value = ["http://bad.com", "http://good.com"]

    mock_send_url_for_check.side_effect = [
        {"matches": [{"threatType": "MALWARE"}]},
        {"matches": []}
    ]
    mock_extract_threat_types.side_effect = lambda resp: [m["threatType"] for m in resp.get("matches", [])]

    any_threat, threat_report = await check_url("some text")

    assert any_threat is True
    assert threat_report == {
        "http://bad.com": ["MALWARE"],
        "http://good.com": []
    }
    assert mock_extract_links.await_count == 1
    assert mock_send_url_for_check.await_count == 2
    assert mock_extract_threat_types.await_count == 2


@pytest.mark.asyncio
@patch("services.check_url.extract_links", new_callable=AsyncMock)
# Test that check_url gracefully handles aiohttp.ClientError exceptions during URL checks.
# The function should catch the error and return None.
async def test_check_url_handles_client_error(mock_extract_links):
    mock_extract_links.return_value = ["http://example.com"]

    with patch("services.check_url.send_url_for_check", side_effect=ClientError("Failed")):
        result = await check_url("some text")
        assert result is None


@pytest.mark.asyncio
@patch("services.check_url.extract_links", new_callable=AsyncMock)
# Test that check_url gracefully handles unexpected exceptions during URL checks.
# The function should catch the exception and return None.
async def test_check_url_handles_unexpected_error(mock_extract_links):
    mock_extract_links.return_value = ["http://example.com"]

    with patch("services.check_url.send_url_for_check", side_effect=Exception("Boom!")):
        result = await check_url("some text")
        assert result is None
