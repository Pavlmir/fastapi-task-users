from fastapi import APIRouter

from app.routers.api_v1 import router as router_v1
from app.routers.common_api import router as common_router

api_router = APIRouter()
api_router.include_router(router_v1, prefix="/v1")
api_router.include_router(common_router, prefix="")
