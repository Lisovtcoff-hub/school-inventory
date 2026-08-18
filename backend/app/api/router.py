from fastapi import APIRouter

from app.api.routes import (
    asset_history,
    assets,
    auth,
    health,
    organizations,
    qr,
    reports,
    users,
)


api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(users.router)
api_router.include_router(assets.router)
api_router.include_router(asset_history.router)
api_router.include_router(qr.router)
api_router.include_router(reports.router)
