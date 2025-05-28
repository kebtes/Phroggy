from aiogram import types
from aiogram.filters import CommandStart

from core.handlers.commands import router

@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "👋 Hello! I’m your group protection assistant.\n"
        "I’ll keep this chat safe from spam, scams, phishing links, and other threats.\n"
        "Add me to a group and make me admin to begin.\n"
        "Use /help to view available commands."
    )
