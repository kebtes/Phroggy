from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.states import HelpStates, MyGroupStates
from core.handlers.callbacks import router
from core.handlers.commands import cmd_help, cmd_my_groups
from core.keyboards import create
from db import groups, users


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
            ["Back", "go_back"]
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

@router.callback_query(HelpStates.main)
async def handle_help(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("group_settings"):
        await send_group_settings(callback, state)

    elif callback.data.startswith("logs"):
        reply_markup = create([
            ["Back", "go_back"]
        ])

        response_msg = (
            "<b><u>Logs</u></b>\n\n"
            "Phroggy keeps a record of every action it takes — whether it's deleting a suspicious message or flagging content. "
            "These logs ensure transparency and give admins and moderators visibility into what’s happening inside the group.\n\n"
            "<b>In-group access</b>\n"
            "• /history to view the last 5 actions directly within the group.\n\n"
            "<b>Full History</b>\n"
            "For a more detailed view, go to the bot in private:\n"
            "/my_groups → Select your group → View History/Logs\n"
            "You'll receive a <code>.txt</code> file with the latest logs (up to 100 entries).\n\n"
            "<b>Note: Only the most recent 100 logs are stored.</b>"
        )

        await state.set_state(HelpStates.logs)

        await callback.message.edit_text(response_msg, reply_markup=reply_markup)

@router.callback_query(HelpStates.group_settings)
async def handle_group_settings(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    if callback.data.startswith("automation_filtering"):
        reply_markup = create([
            ["Back", "go_back"]
        ])

        response_msg = (
            "<b><u>Automation & Filtering</u></b>\n\n"
            "Automation and filtering related commands.\n\n"
            "• /auto_delete + (T/F): If this setting is true, every flagged \n"
            "• /pause_scan + (T/F): If this settings is true, scanning will be permanently stopped. "
            "To get scans back, the admin/moderators should toggle this setting off.\n"
            "• /skip + (file type): If you want to skip certain files from being scanned, "
            "you can call this command by passing the file type as the argument.\n"
            "• /skip + (url): If you want to skip certain links from being scanned, "
            "you can call this command by passing the link as the argument. "
            "Every link that starts with it will be ignored."
        )

        await state.set_state(HelpStates.automation_filtering)

        await callback.message.edit_text(
            response_msg,
            reply_markup=reply_markup
        )

    elif callback.data.startswith("moderation_controls"):
        reply_markup = create([
            ["Back", "go_back"]
        ])

        response_msg = (
            "<b><u>Moderation Control</u></b>\n\n"
            "Moderations control related commands\n\n"
            "• /add_moderator + (username): Adds a user to be a moderator.\n"
            "• /remove_moderator + (username): Removes a user to from being a moderator.\n"
            "• /add_moderator + (username): Adds a user to be a moderator.\n\n"
        )

        await state.set_state(HelpStates.moderation_controls)

        await callback.message.edit_text(response_msg, reply_markup=reply_markup)

    elif callback.data.startswith("detection_sensitivity"):
        reply_markup = create([
            ["Back", "go_back"]
        ])

        response_msg = (
            "<b><u>Detection Sensitivity</u></b>\n\n"
            "Sensitivity related commands\n\n"
            "• /sensitivity + (low | moderate | high): Toggles the sensitvity of the scan. "
            "<i>This only affects spam detection.</i>"
        )

        await state.set_state(HelpStates.detection_sensitivity)

        await callback.message.edit_text(response_msg, reply_markup=reply_markup)

    elif callback.data.startswith("go_back"):
        await callback.bot.delete_message(
            chat_id=user_id,
            message_id=message_id
        )

        await state.clear()

        await cmd_help.help_command(
            callback.message,
            state
        )

@router.callback_query(HelpStates.logs)
async def handle_logs(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.message.chat.id
    message_id = callback.message.message_id

    if callback.data.startswith("go_back"):
        await callback.bot.delete_message(
            chat_id=user_id,
            message_id=message_id
        )

        await state.clear()

        await cmd_help.help_command(
            callback.message,
            state
        )

@router.callback_query(HelpStates.automation_filtering)
async def handle_automation_filtering(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("go_back"):
        await send_group_settings(callback, state)

@router.callback_query(HelpStates.moderation_controls)
async def handle_moderation_controls(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("go_back"):
        await send_group_settings(callback, state)

@router.callback_query(HelpStates.detection_sensitivity)
async def handle_detection_sensitivity(callback: types.CallbackQuery, state: FSMContext):
    if callback.data.startswith("go_back"):
        await send_group_settings(callback, state)

# ---------------------------------------------------------------------------
# -------------------------------UTILS---------------------------------------
# ---------------------------------------------------------------------------

async def send_group_settings(callback: types.CallbackQuery, state: FSMContext):
    reply_markup = create(
            [
                ["Automation & Filtering", "automation_filtering"],
                ["Moderation Controls", "moderation_controls"],
                ["Detection Sensitivity", "detection_sensitivity"],
                ["Back", "go_back"]
            ], per_row=1
        )

    response_msg = (
        "<b><u>Group Settings</u></b>\n\n"
        "Let's help you get around and keep things safe in your group!\n\n"
        "This commands are only available within groups, and only accessible to admin & moderators.\n\n"
        "• <i>Automation & Filtering\n</i>"
        "• <i>Moderation Controls\n</i>"
        "• <i>Detection Sensitivity</i>"
    )

    await callback.message.edit_text(
        response_msg,
        reply_markup=reply_markup
    )

    await state.set_state(HelpStates.group_settings)
