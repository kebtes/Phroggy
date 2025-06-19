from datetime import datetime
from typing import Optional

from pydantic import ValidationError

from db import defaults, schemas
from db.mongo import groups_collection

from loguru import logger
async def group_exists(group_id: int):
    """Returns the group if it exists, else None"""
    try:
        group = await groups_collection.find_one({"group_id": group_id})

    except Exception as e:
        return {"error": "USER_LOOK_UP_FAILED", "data": e}

    return group

async def create_group(group_id: int, group_name: str, admin: int, *, settings: Optional[dict] = None, logs: Optional[dict] = []):
    group = await group_exists(group_id)

    if not group:
        try:
            if not settings:
                settings = schemas.GroupSettings(**defaults.DEFAULT_GROUP_SETTINGS)

            group = schemas.GroupSchema(
                group_id=group_id,
                group_name=group_name,
                admin=admin,
                settings=settings,
                logs=logs
            )

        except ValidationError as e:
            return {"error": "VALIDATION_ERROR", "data" : e}

        await groups_collection.insert_one(group.model_dump())

    return group

async def group_info(group_id: int):
    """Returns the document in the db"""
    try:
        group = await groups_collection.find_one({"group_id": group_id})
        return group if group else []

    except Exception as e:
        logger.exception(e)

async def remove(group_id: int):
    """Assumes the group already exists"""
    try:
        groups = await groups_collection.delete_one({"group_id": group_id})
        return groups

    except Exception as e:
        logger.exception(e)

async def is_admin(group_id: int, user_id: int):
    """Assumes the gorup already exists"""
    try:
        group = await group_info(group_id)
        admin = group.get("admin")
        return user_id == admin
    except Exception:
        # TODO add a logger here
        pass

async def is_moderator(group_id: int, user_name: str):
    """Assumes the gorup already exists"""
    try:
        group = await group_info(group_id)
        moderators = set(group.get("moderators"))
        return user_name in moderators
    except Exception:
        # TODO add a logger here
        pass

async def update(group_id: int, **kwargs):
    """
    Updates group preferences falling under the settings part
    """
    try:
        if "auto_delete" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$set": {"settings.auto_delete": kwargs["auto_delete"]}}
            )

        if "add_moderator" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$push": {"settings.moderators": kwargs["add_moderators"]}}
            )

        if "blacklist_keyword" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$push": {"settings.blacklist_keywords": kwargs["blacklist_keyword"]}}
            )

        if "blacklist" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$push": {"settings.blacklist": kwargs["blacklist"]}}
            )

        if "sensitivity" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$set": {"settings.spam_sensitivity": kwargs["sensitivity"]}}
            )

        if "whitelist" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$push": {"settings.whitelist": kwargs["whitelist"]}}
            )

        if "sensitivity" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$set": {"settings.spam_sensitivity": kwargs["sensitivity"]}}
            )

        if "pause_scan" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$set": {"settings.pause_scan": kwargs["pause_scan"]}}
            )

        if "skip_urls" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$push": {"settings.skip_urls": kwargs["skip_urls"]}}
            )

        if "skip_files" in kwargs:
            await groups_collection.update_one(
                {"group_id": group_id},
                {"$push": {"settings.skip_files": kwargs["skip_files"]}}
            )

    except Exception as e:
        logger.exception(e)

async def log(group_id: int, timestamp: datetime, action: str, user: str, message: str):
    MAX_LOG_SIZE = 50
    log = schemas.GroupLog(
        timestamp=timestamp,
        action=action,
        user=user,
        message=message
    )

    try:
        await groups_collection.update_one(
            {"group_id": group_id},
            {"$push": {
                "logs": {
                    "$each": [log.model_dump()],
                    "$position": 0,
                    "$slice": MAX_LOG_SIZE
                }
            }}
        )

    except Exception as e:
        logger.exception(e)

async def get_log(group_id: int, html_format: bool = True):
    # returns a formatted log in the form of a string

    group = await group_info(group_id)
    logs = group.get("logs", None)

    output = []

    for log in logs:
        timestamp = log["timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        formatted_timestamp = timestamp.strftime("%Y-%m-%d, %H:%M")

        action = log["action"]
        user = log["user"]
        message_text = log["message"]

        if html_format:
            formatted_text = (
                f"• <b>{user} | {action} | <i>{formatted_timestamp}</i></b>\n"
                f"<s>{message_text}</s>\n\n"
            )
        else:
            formatted_text = (
                f"• {user} | {action} | {formatted_timestamp}\n"
                f"{message_text}\n\n"
            )

        output.append(formatted_text)

    return output
