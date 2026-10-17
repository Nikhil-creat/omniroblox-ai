import json
import redis.asyncio as aioredis
from .config import settings

_r = None
def r():
    global _r
    if _r is None:
        _r = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _r

async def remember(session: str, entry: dict, keep: int = 20):
    try:
        await r().lpush(f"sess:{session}", json.dumps(entry))
        await r().ltrim(f"sess:{session}", 0, keep - 1)
    except Exception:
        pass

async def recall(session: str, n: int = 5) -> str:
    try:
        items = await r().lrange(f"sess:{session}", 0, n - 1)
        return "\n".join(json.loads(i).get("spec", "") for i in reversed(items))
    except Exception:
        return ""
