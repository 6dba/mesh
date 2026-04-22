from fastapi import FastAPI

from .api.v1.router import api_router
from .database import Base, engine
from .scheduler import scheduler

app = FastAPI(title="Kosatka Mesh Master")


@app.on_event("startup")
async def startup():
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Start scheduler
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
