from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.v1.router import api_router
from .database import Base, engine
from .scheduler import scheduler, setup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables if they don't exist. This is safe for an MVP; for
    # production, prefer Alembic migrations (not yet set up in this repo).
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # setup_scheduler() registers sync_nodes_job + check_expirations_job
    # and calls scheduler.start() internally. Calling scheduler.start() here
    # directly would leave the scheduler jobless.
    setup_scheduler()
    try:
        yield
    finally:
        scheduler.shutdown()


app = FastAPI(title="Kosatka Mesh Master", lifespan=lifespan)


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
