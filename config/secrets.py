import os

from dotenv import load_dotenv

load_dotenv()

def get_env(key: str, fallback: str = None, required: bool = True):
    value = os.getenv(key, fallback)
    if required and not value:
        raise ValueError(f"{key} not found in environment variables")
    return value


BOT_TOKEN = get_env("BOT_TOKEN", "dummy-bot-token")
VIRUS_TOTAL_API_KEY = get_env("VIRUS_TOTAL_API_KEY", "dummy-virus-api-key")
SAFE_BROWSING_API_KEY = get_env("SAFE_BROWSING_API_KEY", "dummy-safe-browsing-key")
MONGO_DB_CONNECTION_STRING = get_env("MONGO_DB_CONNECTION_STRING", "mongodb://localhost:27017")
BETTER_STACK_INGESTING_HOST = get_env("BETTER_STACK_INGESTING_HOST", "logs.betterstack.dev")
BETTER_STACK_SOURCE_TOKEN = get_env("BETTER_STACK_SOURCE_TOKEN", "dummy-betterstack-token")
WEBHOOK_SECRET = get_env("WEBHOOK_SECRET", "phroggy_secret")

PORT = int(os.getenv("PORT", 3000))
USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
