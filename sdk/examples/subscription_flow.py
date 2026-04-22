import asyncio
import os
from datetime import datetime, timedelta
from kosatka_sdk.client import KosatkaClient
from kosatka_sdk.models import ClientCreate, SubscriptionCreate

async def main():
    base_url = os.getenv("KOSATKA_BASE_URL", "http://localhost:8000")
    api_key = os.getenv("KOSATKA_API_KEY", "your-secret-key")

    client = KosatkaClient(base_url=base_url, api_key=api_key)

    try:
        # 1. Create a client (or get existing)
        external_id = "user_123"
        print(f"--- Creating/Getting Client: {external_id} ---")
        try:
            sdk_client = await client.get_client(external_id)
            print(f"Found existing client ID: {sdk_client.id}")
        except Exception:
            sdk_client = await client.create_client(ClientCreate(
                external_id=external_id,
                email="user@example.com"
            ))
            print(f"Created new client ID: {sdk_client.id}")

        # 2. Create a subscription
        print("--- Creating Subscription ---")
        expires_at = datetime.now() + timedelta(days=30)
        sub = await client.create_subscription(SubscriptionCreate(
            client_id=sdk_client.id,
            plan_name="premium_monthly",
            expires_at=expires_at
        ))
        print(f"Subscription created: ID {sub.id}, Expires {sub.expires_at}")

        # 3. List client subscriptions
        print("--- Active Subscriptions ---")
        subs = await client.get_client_subscriptions(sdk_client.id)
        for s in subs:
            print(f"Plan: {s.plan_name} | Active: {s.is_active} | Expires: {s.expires_at}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
