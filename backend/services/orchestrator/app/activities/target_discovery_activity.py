import httpx
from temporalio import activity
from shared.config import get_settings

settings = get_settings()
ICP_URL = f"http://icp-service:{settings.icp_service_port}/api/v1"


class DiscoverTargetsActivity:
    @activity.defn(name="discover_targets")
    async def run(self, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{ICP_URL}/targets/discover",
                params={"company_id": params["company_id"], "tenant_id": params["tenant_id"]},
            )
            resp.raise_for_status()
            return resp.json()
