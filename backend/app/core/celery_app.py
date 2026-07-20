"""
Celery application instance.

Broker  : Redis (REDIS_URL from env)
Backend : Redis (same instance, different key namespace)

Usage:
  Start worker:  celery -A app.core.celery_app worker --loglevel=info
  Start beat  :  celery -A app.core.celery_app beat   --loglevel=info (Phase 3+)
"""

from celery import Celery

from app.config import get_settings


def create_celery_app() -> Celery:
    settings = get_settings()
    app = Celery(
        "agency_saas",
        broker=settings.redis_url,
        backend=settings.redis_url,
        include=[
            "app.tasks.backfill",
            "app.tasks.report_generation",
        ],
    )
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        # Prevent tasks from silently swallowing exceptions
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )
    return app


celery_app = create_celery_app()


@celery_app.task(name="debug_task", bind=True)
def debug_task(self):  # type: ignore[override]
    """
    Trivial task used in Phase 0 to prove the Celery worker is reachable.
    Call via: debug_task.delay()
    """
    print(f"Debug task executed by worker: {self.request.id}")
    return {"status": "ok", "worker": self.request.hostname}
