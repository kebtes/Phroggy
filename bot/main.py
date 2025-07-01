import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import ClientTimeout, web
from loguru import logger

# Side-effect imports to auto-register handlers
import core.handlers.callbacks.callbacks  # noqa: F401
import core.handlers.commands.cmd_help  # noqa: F401
import core.handlers.commands.cmd_link_group  # noqa: F401
import core.handlers.commands.cmd_my_groups  # noqa: F401
import core.handlers.commands.cmd_scan_file  # noqa: F401
import core.handlers.commands.cmd_scan_url  # noqa: F401
import core.handlers.commands.cmd_start  # noqa: F401
import core.handlers.commands.group_commands.cmd_add_moderators  # noqa: F401
import core.handlers.commands.group_commands.cmd_auto_delete  # noqa: F401
import core.handlers.commands.group_commands.cmd_blacklist  # noqa: F401
import core.handlers.commands.group_commands.cmd_blacklist_kw  # noqa: F401
import core.handlers.commands.group_commands.cmd_history  # noqa: F401
import core.handlers.commands.group_commands.cmd_id  # noqa: F401
import core.handlers.commands.group_commands.cmd_sensitivity  # noqa: F401
import core.handlers.listeners.message_listner  # noqa: F401

# Bot setup
from bot.dispatcher import register_handlers
from bot.set_bot_commands import set_bot_commands
from bot.storage import storage
from config import secrets
from db import mongo
from logger.logger import init_logger, log_sink

# --- Bot Configuration ---
timeout = ClientTimeout(total=60)

bot = Bot(
    token=secrets.BOT_TOKEN,
    timeout=timeout,
    default=DefaultBotProperties(parse_mode="HTML")
)

dp = Dispatcher(storage=storage)
register_handlers(dp)  # Register all command/callback handlers

# --- Webhook Configuration ---
WEBHOOK_PATH = "/api/webhook"
WEBHOOK_SECRET = secrets.WEBHOOK_SECRET
USE_WEBHOOK = secrets.USE_WEBHOOK


# --- Shared Service Initialization ---
async def init_services():
    """
    Initializes logger, bot commands, and MongoDB connection.
    Called once on startup, for both webhook and polling modes.
    """
    await init_logger()
    await set_bot_commands(bot)
    await mongo.init()


# --- Webhook Application Setup ---
def create_app() -> web.Application:
    """
    Creates and configures the aiohttp web application for webhook mode.
    Registers the bot dispatcher, sets up routes, and binds startup/shutdown events.
    """
    logger.info("Starting Phroggy in webhook mode...")
    app = web.Application()
    app.on_startup.append(lambda app: init_services())
    app.on_shutdown.append(lambda app: log_sink.stop())

    # Attach webhook handler
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)

    # Finalize app setup
    setup_application(app, dp, bot=bot)
    return app


# --- Long Polling Startup ---
async def main():
    """
    Starts the bot using long polling (for dev mode or simpler deployment).
    Ensures all services are initialized before polling begins.
    """
    await init_services()
    logger.info("Starting Phroggy in long polling mode...")
    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down polling...")
        await log_sink.stop()

if __name__ == "__main__":
    if USE_WEBHOOK:
        # Run in webhook mode
        app = create_app()
        web.run_app(app, host="0.0.0.0", port=secrets.PORT)
    else:
        # Run in long polling mode
        asyncio.run(main())
