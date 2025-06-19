from aiogram import types
from aiogram.filters import Command, CommandObject
from loguru import logger

from core.handlers.commands import router
from db import groups


@router.message(Command("sensitivity"))
async def id_group(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    group_id = message.chat.id

    if not (await groups.is_admin(group_id, user_id) or await groups.is_moderator(group_id, user_id)):
        await message.reply("Commands are only available to admins/moderators.")
        return

    # check if args is empty
    if not command.args:
        await message.reply("Invalid Format.")
        return

    # check if the arg format is correct
    args = command.args.strip().split()
    if len(args) != 1:
        await message.reply("Invalid Format.")
        return

    try:
        sensitivity = args[0].lower()

        if sensitivity not in ("l", "low", "m", "moderate", "h", "high"):
            await message.reply("Invalid argument.")
            return

        mapping = {
            "l": "low",
            "low": "low",
            "m": "moderate",
            "moderate": "moderate",
            "h": "high",
            "high": "high"
        }
        sensitivity = mapping[sensitivity]

        await groups.update_preference(
            group_id=group_id,
            sensitivity=sensitivity
        )

        await message.reply("Preference updated!")

    except Exception as e:
        logger.exception(e)

