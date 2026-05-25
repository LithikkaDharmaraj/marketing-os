import httpx
from temporalio import activity
from shared.config import get_settings

settings = get_settings()
POSITIONING_URL = f"http://positioning-service:{settings.positioning_service_port}/api/v1"


class GeneratePositioningActivity:
    @activity.defn(name="generate_positioning")
    async def run(self, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{POSITIONING_URL}/positioning/generate",
                params={"company_id": params["company_id"], "tenant_id": params["tenant_id"]},
            )
            resp.raise_for_status()
            return resp.json()
