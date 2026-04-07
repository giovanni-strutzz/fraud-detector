import redis.asyncio as redis
import logging
from typing import Optional
from src.ports.output.repository.AccountRepository import CacheRepository


logger = logging.getLogger(__name__)

class RedisAdapter(CacheRepository):
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        try:
            value = await self.redis_client.get(key)

            return value
        except Exception as exc:
            logger.error(f"Failed to get {key} on Redis: {exc}")

            return None


    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        try:
            await self.redis_client.set(key, value, ex=ttl_seconds)
        except Exception as exc:
            logger.error(f"Failed to set {key} on Redis: {exc}")


    async def close(self):
        await self.redis_client.aclose()