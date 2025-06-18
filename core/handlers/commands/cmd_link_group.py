from uuid import uuid4

from aiogram import types
from aiogram.filters import Command

from core.handlers.commands import router
from db import groups, tokens, users

current_prompts = []

@router.message(Command("link_group"))
async def link_group(message: types.Message):
    uuid = str(uuid4())

    response_msg = (
        "<b>To add this bot to a group, follow the following steps.</b>\n\n"
        "<b> 1.</b> <a href = 'https://t.me/agentivy_bot?startgroup&admin=delete_messages+restrict_members+pin_messages'>Add</a> the bot to the group where you want it to operate.\n\n"
        "<b> 2.</b> Copy and paste the following command with the token inside that group chat. This will activate the bot’s ability to recognize the group.\n\n"
        f"<b>Command:</b> <code><b>/id {uuid}</b></code>\n\n"
        "<b>Token Expires in 10 Minutes</b>"
    )

    user_id = message.chat.id
    await tokens.store_token(uuid, user_id)
    current_prompts.append(await message.reply(response_msg))

# @router.message(AddToGroupStates.waiting_for_id)
async def waiting_for_id(message: types.Message):
    user_id = message.from_user.id
    group_id = message.chat.id

    # group details
    group_info = await message.bot.get_chat(group_id)
    group_name = group_info.title
    group_type = "Public" if group_info.username else "Private"
    active_usernames = group_info.active_usernames
    invite_link = group_info.invite_link

    # user details
    # user_id = message.from_user.id
    user_name = message.from_user.username

    # ! TODO : check if the group is a super group
    # ! some funcitonalities might not work for it

    # create the user
    user = await users.add_group(
        username=user_name,
        user_id=user_id,
        groups=[group_id]
    )

    if "error" in user:
        error = user["error"]

        if error == "VALIDATION_ERROR":
            await message.bot.send_message(user_id, "Error happend while trying to connect the bot to the group. Please try again later...")
            return

    # create the group
    group = await groups.create_group(
        group_id=group_id,
        group_name=group_name,
        admin=user_id
    )

    if "error" in group:
        error = group["error"]

        if error == "VALIDATION_ERROR":
            await message.bot.send_message(user_id, "Error happend while trying to connect the bot to the group. Please try again later...")
            return

    global current_prompts
    for msg in current_prompts:
        await message.bot.delete_message(chat_id=user_id, message_id=msg.message_id)

    response_msg = (
        "<b><u>Bot Successfully Added to Group</u></b>\n\n"
        f"<b>Group Name:</b> {group_name}\n"
        f"<b>Group Type:</b> {group_type}\n"
        f"<b>Active Username:</b> {active_usernames}\n"
        f"<b>Invitation Link:</b> {invite_link}\n\n"
        f"The username <code><b>{user_name}</b></code> has been designated as the group admin, with full access to all bot commands. "
        "Moderators can also be added and will have access to use the bot as well.\n\n"
        "Use the /help command to see all available commands and see how to use this bot within your group."
    )

    await message.bot.send_message(user_id, response_msg)
    current_prompts = []
