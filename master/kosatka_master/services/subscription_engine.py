from datetime import datetime, timezone

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
        # datetime.utcnow() is deprecated in Python 3.12; use a timezone-aware
        # UTC timestamp so comparisons against tz-aware DB columns stay correct.
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        query = (
            update(Subscription)
            .where(Subscription.expires_at < now)
            .where(Subscription.is_active.is_(True))
            .values(is_active=False)
        )
        await self.db.execute(query)
        await self.db.commit()
