from redis import Redis

from .constants import REDIS_URL


def get_redis() -> Redis:
    return Redis.from_url(REDIS_URL)
