import uuid
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from shared.utils.db import get_db
from services.embedding_service.app.service import (
    upsert_icp_profile, upsert_positioning_profile, search_similar, ensure_collections,
    upsert_competitor, search_similar_competitors,
)

router = APIRouter()


@router.on_event("startup")
async def startup():
    await ensure_collections()


@router.post("/embedding/upsert/icp")
async def upsert_icp(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Embed all current ICP profiles for a company into Qdrant."""
    result = await db.execute(
        text("SELECT * FROM icp_profiles WHERE company_id = :cid AND is_current = true"),
        {"cid": str(company_id)},
    )
    rows = result.mappings().all()
    upserted = []
    for row in rows:
        row_dict = dict(row)
        point_id = await upsert_icp_profile(
            icp_id=str(row_dict["id"]),
            tenant_id=str(tenant_id),
            company_id=str(company_id),
            profile_name=row_dict["profile_name"],
            profile_data={
                "firmographics": row_dict.get("firmographics", {}),
                "psychographics": row_dict.get("psychographics", {}),
                "job_titles": row_dict.get("job_titles", []),
                "seniority_levels": row_dict.get("seniority_levels", []),
                "pain_points": row_dict.get("pain_points", []),
                "buying_triggers": row_dict.get("buying_triggers", []),
            },
        )
        await db.execute(
            text("UPDATE icp_profiles SET qdrant_point_id = :pid WHERE id = :id"),
            {"pid": point_id, "id": str(row_dict["id"])},
        )
        upserted.append(point_id)

    # Mark company as fully completed
    await db.execute(
        text("UPDATE companies SET intelligence_status = 'completed' WHERE id = :cid"),
        {"cid": str(company_id)},
    )
    await db.commit()
    return {"upserted": len(upserted), "point_ids": upserted}


class SearchRequest(BaseModel):
    collection: str
    query: str
    tenant_id: uuid.UUID
    limit: int = 5


@router.post("/embedding/search")
async def semantic_search(request: SearchRequest):
    results = await search_similar(
        collection=request.collection,
        query_text=request.query,
        tenant_id=str(request.tenant_id),
        limit=request.limit,
    )
    return {"results": results}


class CompetitorUpsertRequest(BaseModel):
    company_id: str
    tenant_id: str
    competitor_data: dict


class CompetitorSearchRequest(BaseModel):
    query: str
    tenant_id: str
    limit: int = 5


@router.post("/embedding/competitors/upsert")
async def upsert_competitor_endpoint(request: CompetitorUpsertRequest):
    """Embed and store a competitor profile for future similarity searches."""
    point_id = await upsert_competitor(
        company_id=request.company_id,
        tenant_id=request.tenant_id,
        competitor_data=request.competitor_data,
    )
    return {"point_id": point_id, "name": request.competitor_data.get("name")}


@router.post("/embedding/competitors/search")
async def search_competitors_endpoint(request: CompetitorSearchRequest):
    """Find similar competitors by semantic similarity."""
    results = await search_similar_competitors(
        query_text=request.query,
        tenant_id=request.tenant_id,
        limit=request.limit,
    )
    return {"results": results}
