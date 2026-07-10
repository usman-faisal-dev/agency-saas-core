"""
Stub route handlers for Phase 1+ — included here so imports in router.py don't break.
Full implementation arrives in Phase 1 (clients CRUD).
"""
from fastapi import APIRouter

router = APIRouter(prefix="/clients", tags=["clients"])

# Phase 1 will implement:
#   POST   /clients
#   GET    /clients
#   GET    /clients/{client_id}
#   PATCH  /clients/{client_id}
#   DELETE /clients/{client_id}
