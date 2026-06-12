import asyncio
import redis.asyncio as redis
from module.core.tools.log import logger
from module.core.tools.settings import app_settings
import fakeredis.aioredis as fakeredis


class AsyncRedisManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None
        self._pool = None
        self._is_fake = False
        self._lock = asyncio.Lock()

    def get_client(self) -> redis.Redis:
        """
        Instantiates the connection pool configuration layers.
        Does NOT connect or execute blocking network IO on invocation.
        """
        if self.redis is not None:
            return self.redis

        logger.info(f"Configuring real Redis pool parameters: {self.redis_url}")
        self._pool = redis.ConnectionPool.from_url(
            self.redis_url,
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=3.0,
            socket_timeout=3.0
        )
        self.redis = redis.Redis(connection_pool=self._pool)
        self._is_fake = False
        return self.redis

    async def initialize_and_verify(self) -> redis.Redis:
        """
        Asynchronously checks connection health with a retry buffer inside the ASGI lifecycle.
        Gracefully slips into fakeredis mode if real Redis remains entirely unreachable.
        """
        self.get_client()

        if self._is_fake:
            return self.redis

        max_attempts = 3
        ping_timeout = 4.0

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Pinging Redis cache cluster (Attempt {attempt}/{max_attempts})...")
                # Wrap validation ping inside explicit threshold boundaries
                await asyncio.wait_for(self.redis.ping(), timeout=ping_timeout)

                logger.info("Real Redis server connection verified successfully.")
                return self.redis

            except (redis.ConnectionError, redis.TimeoutError, asyncio.TimeoutError, Exception) as e:
                err_text = "TimeoutError" if isinstance(e, asyncio.TimeoutError) else str(e)
                logger.warning(f"Redis verification attempt {attempt} failed: {err_text}")

                if attempt < max_attempts:
                    # Non-blocking backoff delay to allow Docker network bridge translation to settle
                    await asyncio.sleep(1.0)
                else:
                    logger.error("All real Redis verification checks exhausted.")
                    logger.warning("Falling back to fakeredis immediately...")
                    await self._trigger_fakeredis_fallback()

        return self.redis

    async def _trigger_fakeredis_fallback(self):
        """Safely tears down broken pools and spins up an isolated in-memory fakeredis instance."""
        if fakeredis is None:
            raise RuntimeError("Redis server is unreachable and 'fakeredis' package is not installed.")

        # Terminate any partially allocated real connection pools
        if self._pool:
            try:
                await self._pool.disconnect()
            except Exception as e:
                logger.debug(f"Ignored error during broken pool shutdown: {e}")

        self.redis = fakeredis.FakeRedis(decode_responses=True)
        self._is_fake = True
        logger.info("Fakeredis initialized successfully (Isolated In-Memory Mode).")

    async def _get_redis(self) -> redis.Redis:
        """
        Thread-safe runtime guard to guarantee an operational instance is returned.
        Falls back to in-memory mode if the instance state has been corrupted.
        """
        if self.redis is None:
            async with self._lock:
                if self.redis is None:
                    logger.warning("Redis instance was missing at runtime. Initializing fallback...")
                    await self._trigger_fakeredis_fallback()
        return self.redis

    async def disconnect(self):
        """Cleanly releases all active connection pools on worker teardown."""
        async with self._lock:
            if self.redis:
                if self._is_fake:
                    await self.redis.close()
                elif self._pool:
                    await self._pool.disconnect()
                self.redis = None
                logger.info("Redis manager disconnected.")

    async def publish(self, channel: str, message: str):
        redis_client = await self._get_redis()
        return await redis_client.publish(channel, message)

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
        if not ttl:
            await redis_client.mset(mappings)
            return

        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.mset(mappings)
            for key in mappings.keys():
                pipe.expire(key, ttl)
            await pipe.execute()

    async def mget(self, keys: list):
        redis_client = await self._get_redis()
        return await redis_client.mget(keys)

    async def delete(self, key: str):
        redis_client = await self._get_redis()
        await redis_client.delete(key)


async_redis_manager = AsyncRedisManager(app_settings.REDIS_URL)
