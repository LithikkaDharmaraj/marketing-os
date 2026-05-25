import asyncio
import logging
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.models.company import ScrapedPage, ScrapeStatus
from services.scraper_service.app.actors.website_actor import WebsiteActor
from services.scraper_service.app.actors.linkedin_company_actor import LinkedInCompanyActor
from services.scraper_service.app.actors.crunchbase_actor import CrunchbaseActor
from services.scraper_service.app.actors.competitor_actor import CompetitorActor
from services.scraper_service.app.actors.google_search_actor import GoogleSearchActor
from services.scraper_service.app.actors.social_signals_actor import RedditSignalsActor, BuiltWithActor
from services.scraper_service.app.pipeline.normalizer import normalize
from services.scraper_service.app.pipeline.deduplicator import compute_hash

logger = logging.getLogger(__name__)


async def run_full_scrape(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession,
    website_url: str,
    linkedin_url: str | None = None,
    competitors: list[str] = None,
    company_name: str = "",
    industry: str = "",
    domain: str = "",
) -> dict:
    """Launch all scraping actors in parallel and persist results."""
    competitors = competitors or []
    results = {}

    # Fan-out: launch all actors concurrently
    tasks = {
        "website": WebsiteActor().run(url=website_url),
        "google_search": GoogleSearchActor().run(company_name=company_name, domain=domain),
        "reddit": RedditSignalsActor().run(industry=industry),
        "builtwith": BuiltWithActor().run(domain=domain),
    }

    if linkedin_url:
        tasks["linkedin"] = LinkedInCompanyActor().run(linkedin_url=linkedin_url)

    if domain:
        tasks["crunchbase"] = CrunchbaseActor().run(domain=domain)

    for i, competitor_raw in enumerate(competitors[:5]):
        competitor_url = _to_url(competitor_raw)
        if competitor_url:
            tasks[f"competitor_{i}"] = CompetitorActor().run(url=competitor_url)

    # Run all in parallel, capture individual failures
    raw_results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    named_results = dict(zip(tasks.keys(), raw_results))

    for source_key, result in named_results.items():
        source_type = source_key.split("_")[0] if "_" in source_key and source_key.startswith("competitor") else source_key

        if isinstance(result, Exception):
            logger.warning(f"Scrape failed for {source_key}: {result}")
            await _save_scraped_page(
                db, tenant_id, company_id, source_type,
                url=_get_url_for_source(source_key, website_url, linkedin_url, competitors, domain),
                status=ScrapeStatus.failed,
                error=str(result),
            )
            results[source_key] = {"error": str(result)}
            continue

        normalized = normalize(source_type, result.get("structured_data", {}))
        content_hash = result.get("content_hash", "")

        page = await _save_scraped_page(
            db, tenant_id, company_id, source_type,
            url=_get_url_for_source(source_key, website_url, linkedin_url, competitors, domain),
            status=ScrapeStatus.completed,
            structured_data=normalized,
            content_hash=content_hash,
            apify_run_id=result.get("apify_run_id"),
        )
        results[source_key] = normalized

    await db.commit()
    logger.info(f"Scrape complete for company {company_id}: {len(results)} sources")
    return results


async def _save_scraped_page(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    company_id: uuid.UUID,
    source_type: str,
    url: str,
    status: ScrapeStatus,
    structured_data: dict = None,
    content_hash: str = None,
    apify_run_id: str = None,
    error: str = None,
) -> ScrapedPage:
    page = ScrapedPage(
        tenant_id=tenant_id,
        company_id=company_id,
        source_type=source_type,
        source_url=url,
        status=status,
        structured_data=structured_data or {},
        content_hash=content_hash,
        apify_run_id=apify_run_id,
        scraped_at=datetime.utcnow() if status == ScrapeStatus.completed else None,
        error_detail=error,
    )
    db.add(page)
    await db.flush()
    return page


def _to_url(value: str) -> str:
    """Convert a competitor name or URL into a crawlable https URL."""
    if not value:
        return ""
    v = value.strip()
    if v.startswith("http://") or v.startswith("https://"):
        return v
    # Looks like a domain (contains a dot and no spaces)
    if "." in v and " " not in v:
        return f"https://{v}"
    # Plain name — slugify to a likely domain
    slug = v.lower().replace(" ", "").replace(",", "").replace(".", "")
    return f"https://{slug}.com"


def _get_url_for_source(key: str, website_url: str, linkedin_url: str | None, competitors: list[str], domain: str) -> str:
    mapping = {
        "website": website_url,
        "linkedin": linkedin_url or "",
        "crunchbase": f"https://www.crunchbase.com/organization/{domain.split('.')[0]}",
        "google_search": f"https://google.com/search?q={domain}",
        "reddit": "https://reddit.com",
        "builtwith": f"https://builtwith.com/{domain}",
    }
    if key.startswith("competitor_"):
        idx = int(key.split("_")[1])
        return _to_url(competitors[idx]) if idx < len(competitors) else ""
    return mapping.get(key, website_url)
