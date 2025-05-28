import aiohttp

from config.secrets import SAFE_BROWSING_API_KEY
from utils.extract_links import extract_links

API_URL = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={SAFE_BROWSING_API_KEY}"

THREAT_TYPES = [
    "MALWARE",
    "SOCIAL_ENGINEERING",
    "UNWANTED_SOFTWARE",
    "POTENTIALLY_HARMFUL_APPLICATION",
    "THREAT_TYPE_UNSPECIFIED"
]

async def check_url(text: str):
    try:
        links = await extract_links(text)

        if not links:
            return False, {}
        
        threat_report = {}
        any_threat = False

        for link in links:
            response_data = await send_url_for_check(link)
            threat_types = await extract_threat_types(response_data)

            threat_report[link] = threat_types
            if threat_types:
                any_threat = True
        
        return any_threat, threat_report
    
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

async def send_url_for_check(url: str):
    payload = {
        "client": {
            "clientId": "agentivy-bot",
            "clientVersion": "0.1"
        },
        "threatInfo": {
            "threatTypes": THREAT_TYPES,
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=API_URL, json=payload, timeout=30) as resp:
            resp.raise_for_status()
            return await resp.json() 

async def extract_threat_types(response_data: dict):
    matches = response_data.get("matches", [])
    return [match["threatType"] for match in matches]
