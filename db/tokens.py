from typing import Optional, List
from db.mongo import tokens_collection
from db import schemas
from pydantic import ValidationError,UUID4
from datetime import datetime, timezone, timedelta

async def fetch_user_from_token(token: UUID4):
    try:
        result = await tokens_collection.find_one({"token": str(token)})
        if result:
            return result.get("user_id")
        return None
       
    except Exception as e:
        print(f"Error fetching user from token {e}")

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
    