import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN").replace("\\x3a", ":")

VIRUS_TOTAL_API_KEY = os.getenv("VIRUS_TOTAL_API_KEY")

SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY")

MONGO_DB_CONNECTION_STRING = os.getenv("MONGO_DB_CONNECTION_STRING")

BETTER_STACK_INGESTING_HOST = os.getenv("BETTER_STACK_INGESTING_HOST")
BETTER_STACK_SOURCE_TOKEN = os.getenv("BETTER_STACK_SOURCE_TOKEN")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
PORT = int(os.getenv("PORT", 3000))
USE_WEBHOOK = os.getenv('USE_WEBHOOK', 'false').lower() == 'true'

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")

if not VIRUS_TOTAL_API_KEY:
    raise ValueError("VIRUS_TOTAL_API_KEY not found in environment variables")

if not SAFE_BROWSING_API_KEY:
    raise ValueError("SAFE_BROWSING_API_KEY not found in environment variables")

if not MONGO_DB_CONNECTION_STRING:
    raise ValueError("MONGO_DB_CONNECTION_STRING not found in environment variables")

if not BETTER_STACK_INGESTING_HOST:
    raise ValueError("BETTER_STACK_INGESTING_HOST not found in environment variables")

if not BETTER_STACK_SOURCE_TOKEN:
    raise ValueError("BETTER_STACK_SOURCE_TOKEN not found in environment variables")

if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET not found in environment variables")

# if not USE_WEBHOOK:
#     raise ValueError("USE_WEBHOOK not found in environment variables")
