import redis.asyncio as aioredis
from shared.config import get_settings

settings = get_settings()

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_pool


async def publish_event(channel: str, message: str) -> None:
    r = await get_redis()
    await r.publish(channel, message)


async def set_cache(key: str, value: str, ttl_seconds: int = 3600) -> None:
    r = await get_redis()
    await r.setex(key, ttl_seconds, value)


async def get_cache(key: str) -> str | None:
    r = await get_redis()
    return await r.get(key)
