import httpx
from urllib.parse import urlparse
from temporalio import activity
from shared.config import get_settings

settings = get_settings()
SCRAPER_URL = f"http://scraper-service:{settings.scraper_service_port}/api/v1"


def _extract_domain(url: str) -> str:
    """Derive bare domain from a URL."""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        return (parsed.netloc or parsed.path).replace("www.", "").lower()
    except Exception:
        return ""


class ScrapeWebsiteActivity:
    """Single comprehensive scraping activity — passes ALL params so run_full_scrape handles every source."""

    @activity.defn(name="scrape_website")
    async def run(self, params: dict) -> dict:
        website_url = params["website_url"]
        domain = params.get("domain", "") or _extract_domain(website_url)
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{SCRAPER_URL}/scrape/company",
                json={
                    "company_id": params["company_id"],
                    "tenant_id": params["tenant_id"],
                    "website_url": website_url,
                    "linkedin_url": params.get("linkedin_url"),
                    "competitors": params.get("competitors", []),
                    "domain": domain,
                    "company_name": params.get("company_name", ""),
                    "industry": params.get("industry", ""),
                },
            )
            resp.raise_for_status()
            return resp.json()


class ScrapeLinkedInActivity:
    """Kept for worker registration backward compat — scraping is done by ScrapeWebsiteActivity."""

    @activity.defn(name="scrape_linkedin")
    async def run(self, params: dict) -> dict:
        return {"status": "skipped", "note": "Handled by scrape_website activity"}


class ScrapeCrunchbaseActivity:
    """Kept for worker registration backward compat."""

    @activity.defn(name="scrape_crunchbase")
    async def run(self, params: dict) -> dict:
        return {"status": "skipped", "note": "Handled by scrape_website activity"}


class ScrapeCompetitorsActivity:
    """Kept for worker registration backward compat."""

    @activity.defn(name="scrape_competitors")
    async def run(self, params: dict) -> dict:
        return {"status": "skipped", "note": "Handled by scrape_website activity"}


class ScrapePublicSignalsActivity:
    """Kept for worker registration backward compat."""

    @activity.defn(name="scrape_public_signals")
    async def run(self, params: dict) -> dict:
        return {"status": "skipped", "note": "Handled by scrape_website activity"}
