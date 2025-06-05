from config.secrets import MONGO_DB_CONNECTION_STRING
from motor.motor_asyncio import AsyncIOMotorClient 

client = AsyncIOMotorClient(MONGO_DB_CONNECTION_STRING, tls=True)

db = client["main"]
users_collection = db["users"]
groups_collection = db["groups"]
tokens_collection = db["tokens"]

TOKEN_LIFETIME = 600 # seconds

async def init():
    # create indices 
    await users_collection.create_index("user_id")
    await groups_collection.create_index("group_id")
    await tokens_collection.create_index(
        [("created_at", 1)],
        expireAfterSeconds=TOKEN_LIFETIME
    )