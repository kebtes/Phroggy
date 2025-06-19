from aiogram import types
from aiogram.filters import Command, CommandObject
from loguru import logger

from core.handlers.commands import router
from db import groups


@router.message(Command("blacklist"))
async def id_group(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    group_id = message.chat.id

    # only admin can access this command
    if groups.is_admin(group_id, user_id):
        await message.reply("Commmand only available to moderator.")
        return

    # check if args is empty
    if not command.args:
        await message.reply("Please provide a username.")
        return

    # check if the arg format is correct
    args = command.args.strip().split()

    if len(args) != 1:
        await message.reply("Invalid format.")
        return

    try:
        user_name = args[0]
        if not user_name:
            response_msg = (
                "Invalid username. Please try again."
            )
            message.reply(response_msg)
            return

        # !! TODO check if the username is to be blacklisted is already a moderator
        # !! or if the moderator even tried to blacklist the admin

        await groups.update_preference(
            group_id=group_id,
            blacklist = user_name
        )

        await message.reply(
            "Preference Updated!"
        )

    except Exception as e:
        logger.exception(e)

