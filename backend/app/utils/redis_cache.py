import json

from redis import Redis
from redis.exceptions import RedisError

from app.config import settings


def get_redis_client() -> Redis | None:
    try:
        return Redis.from_url(settings.REDIS_URL, decode_responses=True)
    except RedisError:
        return None


def cache_get_json(key: str):
    client = get_redis_client()
    if client is None:
        return None

    try:
        value = client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except (RedisError, ValueError, TypeError):
        return None


def cache_set_json(key: str, value, ttl_seconds: int = 60):
    client = get_redis_client()
    if client is None:
        return

    try:
        client.setex(key, ttl_seconds, json.dumps(value, default=str))
    except (RedisError, TypeError, ValueError):
        return


def cache_delete(key: str):
    client = get_redis_client()
    if client is None:
        return

    try:
        client.delete(key)
    except RedisError:
        return
