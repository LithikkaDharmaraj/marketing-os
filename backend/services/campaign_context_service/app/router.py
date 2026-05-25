import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from shared.utils.db import get_db
from services.campaign_context_service.app.service import generate_campaign_context

router = APIRouter()


@router.post("/campaign/generate")
async def trigger_campaign_context(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    context = await generate_campaign_context(company_id, tenant_id, db)
    return {"status": "completed", "context": context.model_dump()}


@router.get("/campaign/{company_id}")
async def get_campaign_context(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM campaign_context WHERE company_id = :cid AND is_current = true LIMIT 1"),
        {"cid": str(company_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Campaign context not found")
    return dict(row)
