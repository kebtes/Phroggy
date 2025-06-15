from aiogram import types
from aiogram.filters import CommandStart

from core.handlers.commands import router


@router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "<b><u>Phroggy</u></b>\n\n"
        "I’m your AI-powered group guard — built to block shady links, sketchy files, "
        "and also spammy messages using a highly accurate pretrained model.\n\n"
        "Want to see what I can do?\n"
        "Check the /help command and let’s keep your group clean and secure."
    )
