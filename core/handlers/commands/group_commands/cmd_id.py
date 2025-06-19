from aiogram import types
from aiogram.filters import Command, CommandObject
from loguru import logger

from core.handlers.commands import router
from core.handlers.commands.cmd_link_group import waiting_for_id
from db import groups, tokens


@router.message(Command("id"))
async def id_group(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    group_id = message.chat.id
    _user_id = user_id

    # check if the group is already ided
    if await groups.group_exists(group_id):
        response_msg = (
            "<b><u>This group is already linked.</u></b>\n\n"
            "Use the /help command within the bot to view available features and commands."
        )

        await message.reply(response_msg)
        return

    # check if args is empty
    if not command.args:
        await message.reply("Please provide an ID.")
        return

    # check if the arg format is correct
    args = command.args.strip().split()

    if len(args) != 1:
        await message.reply("Invalid format. Please copy & paste exactly the command given in the bot.")
        return

    try:
        token = args[0]
        _user_id = await tokens.fetch_user_from_token(token)

        # no such token, expired or invalid
        if not _user_id:
            response_msg = (
                "Invalid or expired token. Please go back the bot and try connecting again."
            )
            message.reply(response_msg)
            return

    except Exception as e:
        logger.exception(e)

    await waiting_for_id(message)
