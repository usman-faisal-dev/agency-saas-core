"""
Stub models file — imports all models so Alembic can discover them
via metadata when running migrations.

Each model file is kept in its own module (one file per table, per STRUCTURE.md).
This file just ensures they're all registered on Base.metadata.
"""

from app.models.client import Client  # noqa: F401
from app.models.connected_account import ConnectedAccount  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.user import User  # noqa: F401

# Phase 2+ models will be added here as migrations are created:
# from app.models.metrics_daily import MetricsDaily
# from app.models.report import Report
# from app.models.job_run import JobRun
# from app.models.chat_session import ChatSession
# from app.models.chat_message import ChatMessage

__all__ = ["Organization", "User", "Client", "ConnectedAccount"]
