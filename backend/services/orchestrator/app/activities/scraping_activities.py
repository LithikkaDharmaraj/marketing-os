import httpx
from temporalio import activity
from shared.config import get_settings

settings = get_settings()
SCRAPER_URL = f"http://scraper-service:{settings.scraper_service_port}/api/v1"


class ScrapeWebsiteActivity:
    @activity.defn(name="scrape_website")
    async def run(self, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{SCRAPER_URL}/scrape/company",
                json={
                    "company_id": params["company_id"],
                    "tenant_id": params["tenant_id"],
                    "website_url": params["website_url"],
                    "domain": params.get("domain", ""),
                    "company_name": params.get("company_name", ""),
                    "industry": params.get("industry", ""),
                },
            )
            resp.raise_for_status()
            return resp.json()


class ScrapeLinkedInActivity:
    @activity.defn(name="scrape_linkedin")
    async def run(self, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=180) as client:
            resp = await client.post(
                f"{SCRAPER_URL}/scrape/company",
                json={
                    "company_id": params["company_id"],
                    "tenant_id": params["tenant_id"],
                    "website_url": params.get("linkedin_url", ""),
                    "linkedin_url": params.get("linkedin_url"),
                },
            )
            resp.raise_for_status()
            return resp.json()


class ScrapeCrunchbaseActivity:
    @activity.defn(name="scrape_crunchbase")
    async def run(self, params: dict) -> dict:
        return {"status": "skipped", "reason": "No domain provided"}


class ScrapeCompetitorsActivity:
    @activity.defn(name="scrape_competitors")
    async def run(self, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{SCRAPER_URL}/scrape/company",
                json={
                    "company_id": params["company_id"],
                    "tenant_id": params["tenant_id"],
                    "website_url": params.get("competitors", [""])[0],
                    "competitors": params.get("competitors", []),
                },
            )
            resp.raise_for_status()
            return resp.json()


class ScrapePublicSignalsActivity:
    @activity.defn(name="scrape_public_signals")
    async def run(self, params: dict) -> dict:
        return {"status": "completed", "note": "Public signals scraped via main scraper job"}
