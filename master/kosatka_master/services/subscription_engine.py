from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.subscription import Subscription


class SubscriptionEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_subscription(self, client_id: int, plan_name: str, expires_at: datetime):
        subscription = Subscription(client_id=client_id, plan_name=plan_name, expires_at=expires_at)
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription

    async def check_expirations(self):
        now = datetime.utcnow()
        query = (
            update(Subscription)
            .where(Subscription.expires_at < now)
            .where(Subscription.is_active.is_(True))
            .values(is_active=False)
        )
        await self.db.execute(query)
        await self.db.commit()
