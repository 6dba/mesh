import os
import tarfile
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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

# Mount static directory for install.sh
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/api/v1/static/ansible.tar.gz")
async def download_ansible_playbooks(background_tasks: BackgroundTasks):
    """Pack the ansible directory and serve it as a tarball."""
    # Find the root ansible directory (at the project root)
    ansible_dir = Path(__file__).parent.parent.parent / "ansible"

    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=".tar.gz")
    os.close(fd)

    # Pack the directory
    with tarfile.open(temp_path, "w:gz") as tar:
        tar.add(str(ansible_dir), arcname=".")

    # Clean up after sending
    background_tasks.add_task(os.remove, temp_path)

    return FileResponse(temp_path, filename="ansible.tar.gz")


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
