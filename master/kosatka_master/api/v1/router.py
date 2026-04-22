from fastapi import APIRouter
from .nodes import router as nodes_router
from .clients import router as clients_router
from .subscriptions import router as subs_router
from .stats import router as stats_router

api_router = APIRouter()
api_router.include_router(nodes_router)
api_router.include_router(clients_router)
api_router.include_router(subs_router)
api_router.include_router(stats_router)
