"""Celery tasks for the positioning service."""
import asyncio

from shared.celery_app import app
from shared.utils.logging import get_logger

logger = get_logger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.task(
    bind=True,
    name="services.positioning_service.app.tasks.generate_positioning",
    max_retries=3,
    default_retry_delay=60,
    queue="positioning:generate",
)
def generate_positioning_task(self, company_id: str, tenant_id: str):
    """Generates positioning profile for a company."""
    from app.service import generate_positioning

    try:
        logger.info("positioning_task_start", company_id=company_id)
        _run_async(generate_positioning(company_id, tenant_id))
        logger.info("positioning_task_done", company_id=company_id)
    except Exception as exc:
        logger.error("positioning_task_failed", company_id=company_id, error=str(exc))
        raise self.retry(exc=exc)
