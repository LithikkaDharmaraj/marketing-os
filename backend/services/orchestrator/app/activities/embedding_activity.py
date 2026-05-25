import httpx
from temporalio import activity
from shared.config import get_settings

settings = get_settings()
EMBEDDING_URL = f"http://embedding-service:{settings.embedding_service_port}/api/v1"


class EmbedProfilesActivity:
    @activity.defn(name="embed_profiles")
    async def run(self, params: dict) -> dict:
        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(
                f"{EMBEDDING_URL}/embedding/upsert/icp",
                params={"company_id": params["company_id"], "tenant_id": params["tenant_id"]},
            )
            resp.raise_for_status()
            return resp.json()
