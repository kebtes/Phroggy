from typing import List, Optional

from loguru import logger
from pydantic import ValidationError

from db import schemas
from db.mongo import users_collection


async def user_exist(user_id: int):
    """Returns the user if it exists, else None"""
    try:
        user = await users_collection.find_one({"user_id": user_id})

    except Exception as e:
        return {"error": "USER_LOOK_UP_FAILED", "data": e}

    return user

async def create_user(username: str, user_id: int, groups: Optional[List[int]] = None):
    user = await user_exist(user_id)

    if not user:
        try:
            user = schemas.UserSchema(
                username=username,
                user_id=user_id,
                groups=groups or []
            )
            await users_collection.insert_one(user.model_dump())
            return user.model_dump()
        except ValidationError as e:
            return {"error": "VALIDATION_ERROR", "data" : e}

    return user

async def get_groups(user_id: int):
    try:
        user = await users_collection.find_one({"user_id": user_id})
        return user.get("groups", []) if user else []

    except Exception as e:
        logger.exception(e)

async def remove_group(user_id: int, group_id: int):
    try:
        users_collection.update_one(
            {"user_id": user_id},
            {"$pull": {"groups": group_id}}
        )

        return True

    except Exception as e:
        logger.exception(e)

async def add_group(user_name: str, user_id: int, group_id: int):
    try:
        user_exists = await user_exist(user_id)

        if user_exists:
            users_collection.update_one(
                {"user_id": user_id},
                {"$push": {"groups": group_id}}
            )
        else:
            if not user_exists:
                user = await create_user(
                    username=user_name,
                    user_id=user_id,
                    groups=[group_id]
                )

                if "error" in user:
                    raise Exception

        return True

    except Exception as e:
        logger.exception(e)
        raise e
