from datetime import datetime, timezone

from loguru import logger
from pydantic import UUID4, ValidationError

from db import schemas
from db.mongo import tokens_collection


async def fetch_user_from_token(token: UUID4):
    try:
        result = await tokens_collection.find_one({"token": str(token)})
        if result:
            return result.get("user_id")
        return None

    except Exception as e:
        logger.exception(f"Error fetching user from token {e}")

async def store_token(token: UUID4, user_id: int):
    try:
        token_schema = schemas.TokenSchema(
            token=token,
            user_id=user_id,
            created_at=datetime.now(timezone.utc)
        )

        await tokens_collection.insert_one(token_schema.model_dump())

    except ValidationError as e:
        return {"error": "VALIDATION_ERROR", "data": e}
