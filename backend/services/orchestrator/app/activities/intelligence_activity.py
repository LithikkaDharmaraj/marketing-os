import httpx
from temporalio import activity
from shared.config import get_settings

settings = get_settings()
INTELLIGENCE_URL = f"http://intelligence-service:{settings.intelligence_service_port}/api/v1"


class ExtractIntelligenceActivity:
    @activity.defn(name="extract_intelligence")
    async def run(self, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{INTELLIGENCE_URL}/intelligence/extract",
                params={"company_id": params["company_id"], "tenant_id": params["tenant_id"]},
            )
            resp.raise_for_status()
            return resp.json()
