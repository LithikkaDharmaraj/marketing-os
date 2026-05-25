"""Temporal activity: validates and persists the intake record."""
import httpx
from temporalio import activity

from shared.config import get_settings

settings = get_settings()


@activity.defn
async def intake_activity(company_id: str, tenant_id: str) -> dict:
    """Confirms the intake record exists and returns company metadata."""
    url = f"http://intake-service:{settings.intake_service_port}/api/v1/intake/{company_id}"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers={"X-Tenant-ID": tenant_id})
        resp.raise_for_status()
        return resp.json()
