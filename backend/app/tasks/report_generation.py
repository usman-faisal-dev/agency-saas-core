"""
Celery task: async wrapper around the report generation pipeline.
Phase 3 implementation — stub present so Celery worker starts without import errors.
"""

import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.report_generation", bind=True, max_retries=2)
def generate_report_task(self, client_id: str, start_date: str, end_date: str):  # type: ignore[override]
    """
    Async wrapper around reporting/service.py generate_report().
    Full implementation in Phase 3.
    """
    logger.info(
        "Report generation task received: client_id=%s start=%s end=%s",
        client_id,
        start_date,
        end_date,
    )
    # Phase 3: call pillars/reporting/service.py generate_report(...)
    raise NotImplementedError("Report generation implemented in Phase 3")
