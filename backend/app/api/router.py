"""
API v1 root router — aggregates all resource routers.
Registered in main.py under the /api/v1 prefix.

Adding a new resource:
  1. Create backend/app/api/v1/<resource>.py with its APIRouter
  2. Import and include it below — nothing else to change.
"""
from fastapi import APIRouter

from app.api.v1 import (
    chat,
    clients,
    connected_accounts,
    metrics,
    organizations,
    reports,
    upload,
)

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(organizations.router)
v1_router.include_router(clients.router)
v1_router.include_router(connected_accounts.router)
v1_router.include_router(metrics.router)
v1_router.include_router(reports.router)
v1_router.include_router(chat.router)
v1_router.include_router(upload.router)
