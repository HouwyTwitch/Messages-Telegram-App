from fastapi import FastAPI, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import aioredis
from aioredis import Redis

app = FastAPI()

class Message(BaseModel):
    author: str
    content: str

client = AsyncIOMotorClient("mongodb://mongo:27017")
db = client.messages_db
redis = None

@app.on_event("startup")
async def startup():
    global redis
    redis = aioredis.from_url("redis://redis", decode_responses=True)

@app.on_event("shutdown")
async def shutdown():
    await redis.close()

async def get_redis() -> Redis:
    return redis

@app.get("/api/v1/messages/")
async def get_messages(redis: Redis = Depends(get_redis)):
    messages = await redis.get("messages")
    if messages:
        return eval(messages)
    messages = []
    async for message in db.messages.find():
        messages.append({"author": message["author"], "content": message["content"]})
    await redis.set("messages", str(messages))
    return messages

@app.post("/api/v1/message/")
async def post_message(message: Message, redis: Redis = Depends(get_redis)):
    await db.messages.insert_one(message.dict())
    await redis.delete("messages")
    return {"message": "Сообщение получено"}
