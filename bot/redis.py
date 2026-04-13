
from redis.asyncio import Redis

from bot.env import env_config


def get_redis_client() -> Redis:
    return Redis(
        host=env_config.redis.ip,
        port=env_config.redis.port,
        db=env_config.redis.bot,
        decode_responses=True,
        username=env_config.redis.login,
        password=env_config.redis.password
    )
