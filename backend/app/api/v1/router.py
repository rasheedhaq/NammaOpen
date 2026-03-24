from fastapi import APIRouter
from app.api.v1.endpoints import bots, notifications, payments, search, shops, status

api_router = APIRouter()
api_router.include_router(search.router, prefix="/shops", tags=["search"])
api_router.include_router(shops.router, prefix="/shops", tags=["shops"])
api_router.include_router(status.router, prefix="/shops", tags=["status"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(bots.router, prefix="/bots", tags=["bots"])
