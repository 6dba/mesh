from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import settings
from .database import SessionLocal
from .services.node_manager import NodeManager
from .services.subscription_engine import SubscriptionEngine

scheduler = AsyncIOScheduler()


async def sync_nodes_job():
    async with SessionLocal() as db:
        manager = NodeManager(db)
        await manager.sync_all_nodes()


async def check_expirations_job():
    async with SessionLocal() as db:
        engine = SubscriptionEngine(db)
        await engine.check_expirations()


def setup_scheduler():
    scheduler.add_job(sync_nodes_job, "interval", seconds=settings.sync_interval)
    scheduler.add_job(check_expirations_job, "interval", seconds=settings.expiration_check_interval)
    scheduler.start()
