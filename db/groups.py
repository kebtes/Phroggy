from typing import Optional
from db.mongo import groups_collection
from db import schemas, defaults
from pydantic import ValidationError

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
        print(e)

async def remove(group_id: int):
    """Assumes the group already exists"""
    try:
        groups = await groups_collection.delete_one({"group_id": group_id})
        return groups
    
    except Exception as e:
        print(e)
        