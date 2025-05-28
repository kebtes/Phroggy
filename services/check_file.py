from pathlib import Path
import asyncio
import aiohttp
import hashlib
import aiofiles

from config.secrets import VIRUS_TOTAL_API_KEY

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

async def check_file(file_path: str):
    """
    Main entry point to scan a file and return a report and flag status.
    """
    try:
        # check file type before moving forward
        file_extension = Path(file_path).suffix

        if file_extension not in ACCEPTED_FILE_TYPES:
            return ["ERROR_FILE_TYPE_NOT_SUPPORTED"]
        
        analysis_id = await send_file_for_scan(file_path)
        return await get_scan_report(analysis_id)
        
    except Exception as e:
        print(f"[Error] Scan failed: {e}")
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

                file_name = file_path.name
                # data.add_field("file", file_data, filename=file_path.split('/')[-1], content_type="application/octet-stream")
                data.add_field("file", file_data, filename=file_name, content_type="application/octet-stream")

                async with session.post(url, headers=headers, data=data) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    return result["data"]["id"]
                    # return result
    
    except aiohttp.ClientError as e:
        return ("HTTP_ERROR_FAILED_TO_SEND_FILE", str(e))
    
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
                    
                    print(f"[Info] Attempt {attempt + 1}/{max_retries} - Status: {status}")
                    await asyncio.sleep(delay)

            return ("ERROR_FAILED_TO_RESPOND_ON_TIME", None)

        except KeyError:
            return ("KEY_ERROR_MISSING_DATA_ID", None)
        
        except aiohttp.ClientError as e:
            return ("HTTP_ERROR_FAILED_TO_FETCH", str(e))
    
# async def check_if_scan_exists(analysis_id: int):
#     url = f"https://www.virustotal.com/api/v3/files/{file_id}"
#     headers = {'x-apikey': VIRUS_TOTAL_API_KEY}

#     async with aiohttp.ClientSession() as session:
#         try:

async def calc_sha256(file_path: str):
    sha256_hash = hashlib.sha256()

    async with aiofiles.open(file_path, "rb") as f:
        while True:
            chunk = await f.read(8192)
            if not chunk:
                break
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()