"""Celery tasks for the ICP service."""
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
    name="services.icp_service.app.tasks.generate_icps",
    max_retries=3,
    default_retry_delay=60,
    queue="icp:generate",
)
def generate_icps_task(self, company_id: str, tenant_id: str):
    """Generates ICP profiles for a company."""
    from app.service import generate_icps

    try:
        logger.info("icp_task_start", company_id=company_id)
        _run_async(generate_icps(company_id, tenant_id))
        logger.info("icp_task_done", company_id=company_id)
    except Exception as exc:
        logger.error("icp_task_failed", company_id=company_id, error=str(exc))
        raise self.retry(exc=exc)
