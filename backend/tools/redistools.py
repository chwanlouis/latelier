import redis.asyncio as redis
from tools.log import logger
from tools.settings import settings


class AsyncRedisManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    async def _get_redis(self):
        if self.redis is None:
            self.redis = redis.from_url(self.redis_url)
        return self.redis

    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def publish(self, channel: str, message: str):
        redis_client = await self._get_redis()
        await redis_client.publish(channel, message)

    async def subscribe(self, channel: str):
        redis_client = await self._get_redis()
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def get(self, key: str):
        redis_client = await self._get_redis()
        return await redis_client.get(key)

    async def set(self, key: str, value: str, ttl: int = None):
        redis_client = await self._get_redis()
        await redis_client.set(key, value, ex=ttl)

    async def mset(self, mappings: dict, ttl: int = None):
        redis_client = await self._get_redis()
        await redis_client.mset(mappings)
        if ttl is not None:
            for key in mappings.keys():
                await redis_client.expire(key, ttl)

    async def mget(self, keys: list):
        redis_client = await self._get_redis()
        values = await redis_client.mget(keys)
        return [value.decode('utf-8') if value else None for value in values]

    async def delete(self, key: str):
        redis_client = await self._get_redis()
        await redis_client.delete(key)


async_redis_manager = AsyncRedisManager(settings.REDIS_URL)
logger.info(f"Redis manager initialized: {settings.REDIS_URL}")
