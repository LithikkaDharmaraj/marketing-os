import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from shared.utils.db import get_db
from services.icp_service.app.service import generate_icps
from services.icp_service.app.target_discovery import (
    discover_target_companies,
    get_target_companies,
    get_target_contacts,
)

router = APIRouter()


@router.post("/icp/generate")
async def trigger_icp_generation(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    profiles = await generate_icps(company_id, tenant_id, db)
    return {"status": "completed", "count": len(profiles), "profiles": [p.model_dump() for p in profiles]}


@router.get("/icp/{company_id}")
async def get_icps(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM icp_profiles WHERE company_id = :cid AND is_current = true"),
        {"cid": str(company_id)},
    )
    rows = result.mappings().all()
    return [dict(r) for r in rows]


@router.get("/icp/{company_id}/{icp_id}")
async def get_icp(company_id: uuid.UUID, icp_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM icp_profiles WHERE id = :id AND company_id = :cid"),
        {"id": str(icp_id), "cid": str(company_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="ICP not found")
    return dict(row)


@router.post("/targets/discover")
async def trigger_target_discovery(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    companies = await discover_target_companies(company_id, tenant_id, db)
    return {"status": "completed", "count": len(companies)}


@router.get("/targets/{company_id}/companies")
async def list_target_companies(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await get_target_companies(company_id, db)


@router.get("/targets/{company_id}/contacts")
async def list_target_contacts(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await get_target_contacts(company_id, db)


class ICPSearchRequest(BaseModel):
    tenant_id: uuid.UUID
    query: str
    limit: int = 5


@router.post("/icp/search")
async def search_icps(request: ICPSearchRequest):
    """Semantic search in Qdrant for similar ICP profiles."""
    from services.embedding_service.app.service import search_similar
    results = await search_similar(
        collection="icp_profiles",
        query_text=request.query,
        tenant_id=str(request.tenant_id),
        limit=request.limit,
    )
    return {"results": results}
