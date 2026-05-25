"""Celery tasks for the scraper service."""
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
    name="services.scraper_service.app.tasks.run_full_scrape",
    max_retries=3,
    default_retry_delay=30,
    queue="scraper:jobs",
)
def run_full_scrape_task(self, company_id: str, tenant_id: str):
    """Runs the full Apify scraping pipeline for a company."""
    from app.service import run_full_scrape

    try:
        logger.info("scraper_task_start", company_id=company_id)
        _run_async(run_full_scrape(company_id, tenant_id))
        logger.info("scraper_task_done", company_id=company_id)
    except Exception as exc:
        logger.error("scraper_task_failed", company_id=company_id, error=str(exc))
        raise self.retry(exc=exc)


@app.task(
    bind=True,
    name="services.scraper_service.app.tasks.run_competitor_scrape",
    max_retries=3,
    default_retry_delay=30,
    queue="scraper:jobs",
)
def run_competitor_scrape_task(self, company_id: str, competitor_url: str, tenant_id: str):
    """Scrapes a single competitor URL."""
    from app.actors.competitor_actor import CompetitorActor
    from app.service import _save_scraped_page

    try:
        actor = CompetitorActor()
        result = _run_async(actor.run({"url": competitor_url}))
        _run_async(_save_scraped_page(company_id, tenant_id, "competitor", competitor_url, result))
    except Exception as exc:
        logger.error("competitor_scrape_failed", url=competitor_url, error=str(exc))
        raise self.retry(exc=exc)
