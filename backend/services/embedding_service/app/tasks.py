"""Celery tasks for the embedding service."""
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
    name="services.embedding_service.app.tasks.upsert_icp",
    max_retries=3,
    default_retry_delay=30,
    queue="embedding:upsert",
)
def upsert_icp_task(self, icp_profile_id: str, company_id: str, tenant_id: str, profile_data: dict):
    """Embeds and upserts an ICP profile into Qdrant."""
    from app.service import upsert_icp_profile

    try:
        logger.info("embedding_icp_start", icp_id=icp_profile_id)
        _run_async(upsert_icp_profile(icp_profile_id, company_id, tenant_id, profile_data))
        logger.info("embedding_icp_done", icp_id=icp_profile_id)
    except Exception as exc:
        logger.error("embedding_icp_failed", icp_id=icp_profile_id, error=str(exc))
        raise self.retry(exc=exc)


@app.task(
    bind=True,
    name="services.embedding_service.app.tasks.upsert_positioning",
    max_retries=3,
    default_retry_delay=30,
    queue="embedding:upsert",
)
def upsert_positioning_task(self, positioning_id: str, company_id: str, tenant_id: str, profile_data: dict):
    """Embeds and upserts a positioning profile into Qdrant."""
    from app.service import upsert_positioning_profile

    try:
        logger.info("embedding_positioning_start", positioning_id=positioning_id)
        _run_async(upsert_positioning_profile(positioning_id, company_id, tenant_id, profile_data))
        logger.info("embedding_positioning_done", positioning_id=positioning_id)
    except Exception as exc:
        logger.error("embedding_positioning_failed", error=str(exc))
        raise self.retry(exc=exc)
