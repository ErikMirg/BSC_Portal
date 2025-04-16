import json
from typing import Any, Optional
from redis.asyncio import Redis

redis_client = Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def set_cache(key: str, value: Any, expire: int = 60) -> None:
    await redis_client.set(key, json.dumps(value), ex=expire)

async def get_cache(key: str) -> Optional[Any]:
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def delete_cache(key: str) -> None:
    await redis_client.delete(key)
