from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN").replace("\\x3a", ":")
VIRUS_TOTAL_API_KEY = os.getenv("VIRUS_TOTAL_API_KEY")
SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

if not VIRUS_TOTAL_API_KEY:
    raise ValueError("VIRUS_TOTAL_API_KEY not found in environment variables")

if not SAFE_BROWSING_API_KEY:
    raise ValueError("SAFE_BROWSING_API_KEY not found in environment variables")

