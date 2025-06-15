from datetime import datetime, timezone

from aiogram import Router, types

from db import groups
from services.check import check

router = Router()

response_template_flagged = (
    "<b>⚠️ This message was flagged for suspicious content</b>\n\n"
    "<b><u>Reason</u></b>\n"
    "{findings}\n\n"
    "Refrain from interacting!"
)

response_template_deleted = (
    "<b>⚠️ This message was flagged for suspicious content and has been removed.</b>"
)

@router.message(lambda message: message.chat.type in ["group", "supergroup"])
async def handle_messages(message: types.Message):
    document = message.document
    text = message.caption if document else message.text
    group_id = message.chat.id

    group_info = await groups.group_info(group_id)
    group_settings = group_info.get("settings", None)

    blacklisted_usernames = group_settings.get("blacklist", "")
    user_name = message.from_user.username

    if await is_user_blacklisted(user_name, blacklisted_usernames):
        await message.bot.delete_message(
            chat_id=group_id, message_id=message.message_id
        )
        return

    blacklisted_words = group_settings.get("blacklist_keywords", "")
    if await contains_blacklisted_word(text, blacklisted_words):
        await message.bot.delete_message(
            chat_id=group_id, message_id=message.message_id
        )
        return

    result = await check(
        text=text, document=document, group_id=group_id, message=message
    )
    findings = ""
    if result.get("link"):
        findings += "- Suspicious links."
    if result.get("spam"):
        findings += "\n- Contains spam."
    if result.get("file"):
        findings += "\n- Malicious file."

    auto_delete = group_settings.get("auto_delete", None)
    notify = group_settings.get("notify", None)

    if findings:
        await handle_flagged_message(message, findings, auto_delete, notify)

        action = "Removed" if auto_delete else "Flagged"
        await groups.log(
            group_id=group_id,
            timestamp=datetime.now(timezone.utc),
            action=action,
            message=text,
            user=user_name,
        )

async def is_user_blacklisted(user_name, blacklisted_usernames):
    return user_name in blacklisted_usernames


async def contains_blacklisted_word(text, blacklisted_words):
    for word in text.strip().lower().split():
        if word in blacklisted_words:
            return True
    return False


async def handle_flagged_message(message, findings, auto_delete, notify):
    if notify:
        if auto_delete:
            response_msg = response_template_deleted.format(findings=findings)
            await message.reply(response_msg)
        else:
            response_msg = response_template_flagged.format(findings=findings)
            await message.reply(response_msg)

    if auto_delete:
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id
        )
