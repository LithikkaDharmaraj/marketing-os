"""Celery tasks for the intelligence service."""
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
    name="services.intelligence_service.app.tasks.extract_intelligence",
    max_retries=3,
    default_retry_delay=60,
    queue="intelligence:extract",
)
def extract_intelligence_task(self, company_id: str, tenant_id: str):
    """Runs Groq intelligence extraction for a company."""
    from app.service import extract_business_intelligence

    try:
        logger.info("intelligence_task_start", company_id=company_id)
        _run_async(extract_business_intelligence(company_id, tenant_id))
        logger.info("intelligence_task_done", company_id=company_id)
    except Exception as exc:
        logger.error("intelligence_task_failed", company_id=company_id, error=str(exc))
        raise self.retry(exc=exc)
