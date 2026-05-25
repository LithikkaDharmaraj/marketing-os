import uuid
import logging
from typing import Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue,
)
from sentence_transformers import SentenceTransformer
from shared.config import get_settings
from services.embedding_service.app.collections import COLLECTIONS

logger = logging.getLogger(__name__)
settings = get_settings()

_qdrant_client: AsyncQdrantClient | None = None
_embedding_model: SentenceTransformer | None = None


def get_qdrant() -> AsyncQdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )
    return _qdrant_client


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    return model.encode(text, normalize_embeddings=True).tolist()


async def ensure_collections() -> None:
    """Create Qdrant collections if they don't exist."""
    client = get_qdrant()
    existing = await client.get_collections()
    existing_names = {c.name for c in existing.collections}

    for name, config in COLLECTIONS.items():
        if name not in existing_names:
            await client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=config["size"],
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {name}")


async def upsert_icp_profile(
    icp_id: str,
    tenant_id: str,
    company_id: str,
    profile_name: str,
    profile_data: dict,
) -> str:
    """Embed and upsert an ICP profile into Qdrant."""
    text_for_embedding = _icp_to_text(profile_name, profile_data)
    vector = embed_text(text_for_embedding)
    point_id = str(uuid.uuid4())

    client = get_qdrant()
    await client.upsert(
        collection_name="icp_profiles",
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "tenant_id": tenant_id,
                    "company_id": company_id,
                    "icp_id": icp_id,
                    "profile_name": profile_name,
                    "text_summary": text_for_embedding[:500],
                    "industries": profile_data.get("firmographics", {}).get("industries", []),
                    "seniority": profile_data.get("seniority_levels", []),
                },
            )
        ],
    )
    logger.info(f"Upserted ICP {icp_id} to Qdrant, point_id={point_id}")
    return point_id


async def upsert_positioning_profile(
    positioning_id: str,
    tenant_id: str,
    company_id: str,
    profile_data: dict,
) -> str:
    core = profile_data.get("core_positioning", {})
    text_for_embedding = (
        f"{core.get('statement', '')} "
        f"{core.get('category', '')} "
        f"{' '.join(profile_data.get('competitive_moats', []))}"
    )
    vector = embed_text(text_for_embedding)
    point_id = str(uuid.uuid4())

    client = get_qdrant()
    await client.upsert(
        collection_name="positioning_profiles",
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "tenant_id": tenant_id,
                    "company_id": company_id,
                    "positioning_id": positioning_id,
                    "category": core.get("category", ""),
                    "text_summary": text_for_embedding[:500],
                },
            )
        ],
    )
    return point_id


async def search_similar(
    collection: str,
    query_text: str,
    tenant_id: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Semantic similarity search with tenant isolation."""
    client = get_qdrant()
    vector = embed_text(query_text)

    results = await client.search(
        collection_name=collection,
        query_vector=vector,
        query_filter=Filter(
            must=[FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id))]
        ),
        limit=limit,
        with_payload=True,
    )

    return [
        {
            "id": str(r.id),
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]


async def upsert_competitor(
    company_id: str,
    tenant_id: str,
    competitor_data: dict,
) -> str:
    """Embed and upsert a discovered competitor into the competitors Qdrant collection."""
    name = competitor_data.get("name", "")
    text = _competitor_to_text(competitor_data)
    vector = embed_text(text)
    point_id = str(uuid.uuid4())

    client = get_qdrant()
    await client.upsert(
        collection_name="competitors",
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "company_id": company_id,
                    "tenant_id": tenant_id,
                    "name": name,
                    "website": competitor_data.get("website", ""),
                    "category": competitor_data.get("category", ""),
                    "industry_tags": competitor_data.get("target_audience", [])[:3],
                    "competitor_type": competitor_data.get("competitor_type", "direct"),
                    "text_summary": text[:500],
                    "competitor_data": competitor_data,
                },
            )
        ],
    )
    logger.info(f"Upserted competitor '{name}' to Qdrant, point_id={point_id}")
    return point_id


async def search_similar_competitors(
    query_text: str,
    tenant_id: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Find similar competitors across the global competitors collection (not tenant-scoped)."""
    client = get_qdrant()
    vector = embed_text(query_text)

    results = await client.search(
        collection_name="competitors",
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )

    return [
        {
            "id": str(r.id),
            "score": r.score,
            "payload": r.payload,
        }
        for r in results
    ]


def _competitor_to_text(data: dict) -> str:
    return (
        f"Competitor: {data.get('name', '')}. "
        f"Category: {data.get('category', '')}. "
        f"Positioning: {data.get('positioning', '')}. "
        f"Target: {', '.join(data.get('target_audience', [])[:3])}. "
        f"Features: {', '.join(data.get('core_features', [])[:3])}. "
        f"Pricing: {data.get('pricing_model', '')}."
    )


def _icp_to_text(profile_name: str, data: dict) -> str:
    firmographics = data.get("firmographics", {})
    psychographics = data.get("psychographics", {})
    pain_points = [p.get("pain", "") if isinstance(p, dict) else str(p) for p in data.get("pain_points", [])]

    return (
        f"ICP: {profile_name}. "
        f"Industries: {', '.join(firmographics.get('industries', []))}. "
        f"Roles: {', '.join(data.get('job_titles', [])[:3])}. "
        f"Goals: {', '.join(psychographics.get('goals', [])[:2])}. "
        f"Fears: {', '.join(psychographics.get('fears', [])[:2])}. "
        f"Pain points: {', '.join(pain_points[:3])}. "
        f"Buying triggers: {', '.join(data.get('buying_triggers', [])[:3])}."
    )
