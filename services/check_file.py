import asyncio
import threading
from pathlib import Path

import aiofiles
import aiohttp
from loguru import logger

from config.secrets import VIRUS_TOTAL_API_KEY
from utils.file_protection import password_protected

# from utils.hash_calc import calc_sha256

CATEGORIES = ['malicious', 'suspicious']
ACCEPTED_FILE_TYPES = [
    # Executables & Binaries
    ".exe", ".dll", ".msi", ".sys", ".scr", ".com", ".bat",
    "ELF", "Mach-O",

    # Documents
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".pdf", ".rtf", ".txt", ".odt",

    # Archives
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2",

    # Media
    ".jpg", ".png", ".gif", ".bmp", ".ico",
    ".mp3", ".mp4", ".avi", ".mkv",

    # Scripts and Code
    ".js", ".vbs", ".ps1", ".py", ".sh",
    ".java", ".class", ".jar",

    # Other
    ".apk", ".iso", ".img", ".bin", ".hex", ".ps", ".lnk"
]

MAX_REQ_PER_MIN = 4

class RateLimitedChecker:
    """
    RateLimitedChecker is a utility that enforces a rate limit on asynchronous tasks,
    such as API requests. It ensures that no more than MAX_REQ_PER_MIN tasks are
    processed in a given 60-second interval.

    Tasks are enqueued via `enqueue_task(file_path)` and processed in the background
    by a worker loop. If the rate limit is reached, the worker waits until the limit
    is reset before continuing. A separate thread resets the request counter every 60 seconds.
    """
    def __init__(self):
        self.max_requests = MAX_REQ_PER_MIN
        self.requests_left = self.max_requests
        self.queue = asyncio.Queue()
        self.interval = 60
        self.lock = threading.Lock()
        self.worker_running = False

        threading.Thread(target=self._start_reset_loop, daemon=True).start()

    async def __call__(self, file_path: str):
        return await self.enqueue_task(file_path)

    def _start_reset_loop(self):
        """Background thread that resets the request counter every minute."""
        while True:
            threading.Event().wait(self.interval)
            with self.lock:
                self.requests_left = self.max_requests

    async def enqueue_task(self, file_path: str):
        future = asyncio.get_event_loop().create_future()
        await self.queue.put((file_path, future))
        await self.start_worker()
        return await future

    async def process_queue(self):
        while True:
            if self.queue.empty():
                await asyncio.sleep(0.1)
                continue

            with self.lock:
                if self.requests_left > 0:
                    self.requests_left -= 1
                else:
                    await asyncio.sleep(1)
                    continue

            file_path, future = await self.queue.get()
            asyncio.create_task(self._run_scan(file_path, future))

    async def start_worker(self):
        if self.worker_running:
            return

        asyncio.create_task(self.process_queue())
        self.worker_running = True

    async def _run_scan(self, file_path: str, future):
        try:
            result = await check_file(file_path)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)

scanner = RateLimitedChecker()

async def check_file(file_path: str):
    """
    Main entry point to scan a file and return a report and flag status.
    """

    COMPRESSED_FILE_TYPES = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]

    try:

        # check file type before moving forward
        file_extension = Path(file_path).suffix

        if file_extension not in ACCEPTED_FILE_TYPES:
            return {"error": "ERROR_FILE_TYPE_NOT_SUPPORTED", "file_type": file_extension}

        if file_extension in COMPRESSED_FILE_TYPES:
            try:
                if password_protected(file_extension):
                    return {"error": "ERROR_PASSWORD_PROTECTED", "file_type": file_extension}

            except ValueError:
                pass

        # Check if a scan for the file already exists by sending a GET request using its SHA-256 hash
        # sha256 = await calc_sha256(str(file_path))
        # response = await get_result_by_sha256(sha256)

        # if "error" in response and response["error"] == "NOT_FOUND":
        #     analysis_id = await send_file_for_scan(file_path)
        #     return await get_scan_report(analysis_id)

        # return await get_result_by_sha256(sha256)

        analysis_id = await send_file_for_scan(file_path)
        return await get_scan_report(analysis_id)

    except Exception as e:
        logger.log(f"[Error] Scan failed: {e}")
        return None

async def send_file_for_scan(file_path: str):
    """
    Uploads a file to VirusTotal and returns the id of scan initiation response.
    """

    url = 'https://www.virustotal.com/api/v3/files'
    headers = {'x-apikey': VIRUS_TOTAL_API_KEY}

    try:
        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(file_path, "rb") as f:
                file_data = await f.read()
                data = aiohttp.FormData()

                file_name = Path(file_path).name
                data.add_field("file", file_data, filename=file_name, content_type="application/octet-stream")

                async with session.post(url, headers=headers, data=data) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    return result["data"]["id"]
                    # return result

    except aiohttp.ClientError as e:
        return ("CLIENT_ERROR", str(e))

    except aiohttp.ContentTypeError:
        return ("JSON_ERROR_FAILED_TO_PARSE_ERROR")


async def get_scan_report(analysis_id: int, max_retries: int = 20, delay: int = 3) -> dict:
    """
    Polls VirusTotal until the scan report is ready or timeout is reached.
    """
    url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = {'x-apikey': VIRUS_TOTAL_API_KEY}

    async with aiohttp.ClientSession() as session:
        try:
            for attempt in range(max_retries):
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()

                    status = result.get("data", {}).get("attributes", {}).get("status")
                    if status == "completed":
                        return result

                    # print(f"[Info] Attempt {attempt + 1}/{max_retries} - Status: {status}")
                    await asyncio.sleep(delay)

            return {"error": "ERROR_FAILED_TO_RESPOND_ON_TIME"}

        except KeyError:
            return ("KEY_ERROR_MISSING_DATA_ID", None)

        except aiohttp.ClientError as e:
            return {"error": "CLIENT_ERROR", "data": str(e)}

async def get_result_by_sha256(sha256: str):
    url = f"https://www.virustotal.com/api/v3/files/{sha256}"
    headers = {'x-apikey': VIRUS_TOTAL_API_KEY}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=url, headers=headers) as response:
                response.raise_for_status()
                result : dict = await response.json()

                error = result.get("error")
                if isinstance(error, dict) and error.get("code") == "NotFoundError":
                    return {"error": "NOT_FOUND"}

                return result

        except aiohttp.ClientError as e:
            return {"error": "CLIENT_ERROR", "data": str(e)}
