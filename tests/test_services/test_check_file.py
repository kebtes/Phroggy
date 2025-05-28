import pytest
from unittest.mock import patch, AsyncMock, MagicMock, ANY

import services.check_file 

@pytest.mark.asyncio
async def test_check_file_rejects_unsupported_file():
    # Provide unsupported extension
    result = await services.check_file.check_file("sample.unsupportedext")
    assert result == {"error": "ERROR_FILE_TYPE_NOT_SUPPORTED", "file_type": ANY}

@pytest.mark.asyncio
@patch("services.check_file.send_file_for_scan", new_callable=AsyncMock)
@patch("services.check_file.get_scan_report", new_callable=AsyncMock)
async def test_check_file_success(mock_get_scan_report, mock_send_file_for_scan):
    # Mock the scan functions
    mock_send_file_for_scan.return_value = "file_id_123"
    mock_get_scan_report.return_value = {"data": "scan_report"}

    result = await services.check_file.check_file("sample.pdf")
    assert result == {"data": "scan_report"}
    mock_send_file_for_scan.assert_called_once_with("sample.pdf")
    mock_get_scan_report.assert_called_once_with("file_id_123")

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.post")
@patch("aiofiles.open")
async def test_send_file_for_scan_success(mock_aiofiles_open, mock_post):
    # Mock reading file data async
    mock_file = AsyncMock()
    mock_file.read = AsyncMock(return_value=b"filedata")
    mock_aiofiles_open.return_value.__aenter__.return_value = mock_file

    # Mock aiohttp response
    mock_resp = AsyncMock()
    mock_resp.json = AsyncMock(return_value={"data": {"id": "123abc"}})
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value.__aenter__.return_value = mock_resp

    result = await services.check_file.send_file_for_scan("sample.pdf")
    assert result == "123abc"

@pytest.mark.asyncio
@patch("aiohttp.ClientSession.get")
async def test_get_scan_report_success(mock_get):
    # Simulate two attempts: first incomplete, second complete
    incomplete_resp = AsyncMock()
    incomplete_resp.json = AsyncMock(return_value={
        "data": {"attributes": {"status": "queued"}}
    })
    incomplete_resp.raise_for_status = MagicMock()

    complete_resp = AsyncMock()
    complete_resp.json = AsyncMock(return_value={
        "data": {"attributes": {"status": "completed"}, "result": "good"}
    })
    complete_resp.raise_for_status = MagicMock()

    mock_get.side_effect = [async_context_manager(incomplete_resp),
                            async_context_manager(complete_resp)]

    # Patch asyncio.sleep to speed up test
    with patch("asyncio.sleep", new=AsyncMock()):
        result = await services.check_file.get_scan_report("file_id", max_retries=3, delay=0)
    assert result["data"]["attributes"]["status"] == "completed"

# Helper to make async context manager from mock response
class async_context_manager:
    def __init__(self, obj):
        self.obj = obj
    async def __aenter__(self):
        return self.obj
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
