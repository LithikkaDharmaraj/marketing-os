import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Any
import httpx
from shared.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

APIFY_BASE = settings.apify_base_url


class BaseApifyActor(ABC):
    """Base class for all Apify-backed scraping actors."""

    actor_id: str = ""
    timeout_seconds: int = 600
    max_retries: int = 3

    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.apify_api_key}"},
            timeout=30.0,
        )

    @abstractmethod
    def build_input(self, **kwargs) -> dict:
        """Return the Apify actor input JSON."""

    @abstractmethod
    def normalize(self, raw_items: list[dict]) -> dict:
        """Map raw Apify output to a normalized structured_data dict."""

    async def run(self, **kwargs) -> dict[str, Any]:
        """Launch actor, poll until done, return normalized data + metadata."""
        actor_input = self.build_input(**kwargs)

        for attempt in range(1, self.max_retries + 1):
            try:
                run_id = await self._start_run(actor_input)
                result = await self._poll_run(run_id)
                items = await self._fetch_dataset(result["defaultDatasetId"])
                normalized = self.normalize(items)
                content_hash = _hash_content(str(items))
                return {
                    "apify_run_id": run_id,
                    "actor_id": self.actor_id,
                    "items_count": len(items),
                    "structured_data": normalized,
                    "content_hash": content_hash,
                    "raw_items": items[:5],  # sample for debugging
                }
            except Exception as e:
                logger.warning(f"Actor {self.actor_id} attempt {attempt} failed: {e}")
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(2 ** attempt)

    async def _start_run(self, actor_input: dict) -> str:
        resp = await self.client.post(
            f"{APIFY_BASE}/acts/{self.actor_id}/runs",
            json=actor_input,
        )
        resp.raise_for_status()
        return resp.json()["data"]["id"]

    async def _poll_run(self, run_id: str) -> dict:
        poll_interval = 2
        elapsed = 0
        while elapsed < self.timeout_seconds:
            resp = await self.client.get(f"{APIFY_BASE}/actor-runs/{run_id}")
            resp.raise_for_status()
            data = resp.json()["data"]
            status = data["status"]
            if status == "SUCCEEDED":
                return data
            if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                raise RuntimeError(f"Apify run {run_id} ended with status: {status}")
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        raise TimeoutError(f"Apify run {run_id} timed out after {self.timeout_seconds}s")

    async def _fetch_dataset(self, dataset_id: str) -> list[dict]:
        resp = await self.client.get(
            f"{APIFY_BASE}/datasets/{dataset_id}/items",
            params={"format": "json", "limit": 200},
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self.client.aclose()


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()
