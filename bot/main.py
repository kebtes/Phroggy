import asyncio
from aiohttp import ClientTimeout

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from bot.dispatcher import register_handlers
from bot.set_bot_commands import set_bot_commands
from bot.storage import storage
from core.handlers.commands import (
    cmd_scan_file,
    cmd_scan_url,
    cmd_start,
    cmd_link_group,
    cmd_my_groups
)
from core.handlers.commands.group_commands import (
    cmd_id,
)

from db import mongo

from core.handlers.callbacks import callbacks

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