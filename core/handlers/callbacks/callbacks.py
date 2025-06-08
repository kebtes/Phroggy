from aiogram import types
from aiogram.fsm.context import FSMContext

from core.handlers.callbacks import router
from db import groups, users
from core.keyboards import create
from bot.states import MyGroupStates
from core.handlers.commands import cmd_my_groups

@router.callback_query(MyGroupStates.waiting_for_group_choice)
async def handle_link_group_callback(callback : types.CallbackQuery, state: FSMContext):
    tail = ":".join(callback.data.split(":")[1:])
    scope, id = tail.split(":")

    if scope == "group":
        group_id = int(id)

        # Fetch group info
        group_info = await callback.message.bot.get_chat(group_id)
        group_name = group_info.title
        group_type = "Public" if group_info.username else "Private"
        active_usernames = group_info.active_usernames
        invite_link = group_info.invite_link

        # Fetch admin info from DB
        db_info = await groups.group_info(group_id)
        admin_id = db_info.get("admin")
        
        # Fetch admin username
        admin_chat = await callback.message.bot.get_chat(admin_id)
        user_name = admin_chat.username or f"{admin_chat.first_name} {admin_chat.last_name or ''}".strip()

        # some more infos for msg
        moderators = db_info.get("moderators")
        blacklist = db_info.get("blacklist")
        whitelist = db_info.get("whitelist")

        buttons = [
            ["Remove", f"remove:group:{group_id}"],
            # ["Change Admin", f"change:admin:{group_id}"],
            ["Back", f"go_back"]
        ]

        reply_markup = create(
            buttons=buttons,
            per_row=2
        ) 
        response_msg = (
            "<b><u>Group Information</u></b>\n\n"
            f"<b>Group Name:</b> {group_name}\n"
            f"<b>Group Type:</b> {group_type}\n"
            f"<b>Active Username:</b> {active_usernames}\n"
            f"<b>Moderators:</b> {moderators}\n"
            f"<b>Blacklisted Usernames:</b> {blacklist}\n"
            f"<b>Whitelisted Usernames:</b> {whitelist}\n"
            f"<b>Invitation Link:</b> {invite_link}\n\n"
        )

        await callback.message.edit_text(response_msg, reply_markup=reply_markup)
        await state.set_state(MyGroupStates.waiting_for_actions)

@router.callback_query(MyGroupStates.waiting_for_actions)
async def handle_actions(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("remove:group"):
        *_, group_id = callback.data.lower().split(":")
        group_id = int(group_id)
        user_id = callback.from_user.id

        await groups.remove(group_id)
        await users.remove_group(user_id, group_id)

        await callback.message.edit_text("Group removed successfully.")
        await state.clear()

    elif callback.data.startswith("change"):
        # change admin logic here
        pass

    elif callback.data.startswith("go_back"):
        await callback.bot.delete_message(callback.message.chat.id, callback.message.message_id)
        await state.clear()
        await cmd_my_groups.list_groups(callback.message, state)

    await state.set_state(MyGroupStates.waiting_approval_group_deletion)