import asyncio
from aiohttp import ClientTimeout

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from bot.dispatcher import register_handlers
from bot.set_bot_commands import set_bot_commands
from bot.storage import storage
from db import mongo

# Command Handlers (side-effect imports for registration)
import core.handlers.commands.cmd_scan_file  # noqa: F401
import core.handlers.commands.cmd_scan_url  # noqa: F401
import core.handlers.commands.cmd_start  # noqa: F401
import core.handlers.commands.cmd_link_group  # noqa: F401
import core.handlers.commands.cmd_my_groups  # noqa: F401
import core.handlers.commands.group_commands.cmd_id  # noqa: F401
import core.handlers.message_listner  # noqa: F401

# Callback Handlers
import core.handlers.callbacks.callbacks  # noqa: F401

timeout = ClientTimeout(total=60)

async def main():
    bot = Bot(token=BOT_TOKEN, timeout=timeout, default=DefaultBotProperties(parse_mode="HTML"))
    
    dp = Dispatcher(storage=storage)

    register_handlers(dp)
    await set_bot_commands(bot)
    
    print("Bot is up and running...")
    await dp.start_polling(bot)

    # db logics
    await mongo.init()

if __name__ == '__main__':
    asyncio.run(main())