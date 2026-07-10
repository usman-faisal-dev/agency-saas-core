"""
Celery task: 60-day historical backfill.
Phase 2 implementation — stub present so Celery worker starts without import errors.
"""
import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.backfill", bind=True, max_retries=3)
def run_backfill(self, client_id: str, provider: str):  # type: ignore[override]
    """
    Enqueue a 60-day historical metrics backfill for a client + provider.
    Full implementation in Phase 2.
    """
    logger.info("Backfill task received: client_id=%s provider=%s", client_id, provider)
    # Phase 2: call integrations layer, write metrics_daily rows, log job_runs
    raise NotImplementedError("Backfill implemented in Phase 2")
