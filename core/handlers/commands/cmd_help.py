from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import HelpStates
from core import keyboards
from core.handlers.commands import router


@router.message(Command("help"))
async def help_command(message: types.Message, state: FSMContext):
    reply_markup = keyboards.create([
        ["Group Settings", "group_settings"],
        ["Logs", "logs"]
    ])

    await message.answer(
        "<b><u>Help</u></b>\n\n"
        "Below are the list of commands you will find using this command in a private chat!\n\n"
        "<b>General Commands</b>\n"
        "• /start: Starts me!\n"
        "• /help: Sends this message.\n\n"
        "<b>Quick Scanners</b>\n"
        "• /scan_file: Forward/upload a file to scan it for potential malware. "
        "I’ll check it against 20+ top antivirus engines and give you a detailed report of any threats found.\n"
        "• /scan_url: Forward/upload a link containing message to see if it's any sketchy.\n\n"
        "<b>Groups</b>\n"
        "• /link_group: Attach me to your group and unlock Phroggy’s full power!\n"
        "• /my_groups: See all the groups you’ve linked me to."
        "From here, you can unlink groups, access log history, and manage other settings effortlessly.",
        reply_markup=reply_markup
    )

    await state.set_state(HelpStates.main)
