import redis
import json
import hashlib
from app.config import REDIS_URL

# Redis connection (from .env or docker-compose)
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def _make_cache_key(prefix: str, params: dict) -> str:
    key_string = json.dumps(params, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


def get_cached_result(prefix: str, params: dict):
    key = _make_cache_key(prefix, params)
    result = r.get(key)
    if result:
        return json.loads(result)
    return None


def set_cached_result(prefix: str, params: dict, data: dict, ttl: int = 3600):
    key = _make_cache_key(prefix, params)
    r.setex(key, ttl, json.dumps(data, ensure_ascii=False))
