from aiogram import types
from aiogram.filters import Command

from core.handlers.commands import router
from db import groups


@router.message(Command("history"))
async def id_group(message: types.Message):
    group_id = message.chat.id

    if await groups.group_exists(group_id):
        await message.reply(
            "<b>Phroggy hasn't been linked to the group yet.</b>\n\n"
            "Go to the bot and link the group first, @Phroggy_Bot"
        )
        return

    logs = await groups.get_log(group_id)

    if logs:
        response_msg = "Only the last 5 logs will be shown here. Options to get more logs will be available inside of the bot.\n\n"
        response_msg += "".join(logs[:5])
    else:
        response_msg = "No logs so far!"

    await message.answer(response_msg)
