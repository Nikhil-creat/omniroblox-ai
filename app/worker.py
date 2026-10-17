import asyncio
from celery import Celery
from .config import settings
from .groq_router import router
from . import agents

celery_app = Celery("omni", broker=settings.redis_url, backend=settings.redis_url)

@celery_app.task
def build_task(spec: str) -> dict:
    async def run():
        await router.discover()
        return await agents.build_feature(spec)
    return asyncio.run(run())
