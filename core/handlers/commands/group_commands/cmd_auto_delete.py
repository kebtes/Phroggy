from aiogram import types
from aiogram.filters import Command, CommandObject
from loguru import logger

from core.handlers.commands import router
from db import groups


@router.message(Command("auto_delete"))
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
        auto_delete = args[0].lower()

        if auto_delete not in ("t", "true", "f", "false"):
            await message.reply("Options are either t/f")
            return

        auto_delete = (auto_delete == "t" or auto_delete == "true")
        await groups.update_preference(
            group_id=group_id,
            auto_delete=auto_delete
        )

        await message.reply("Preference updated!")

    except Exception as e:
        logger.exception(e)

