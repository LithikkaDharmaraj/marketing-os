import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from shared.utils.db import get_db
from services.positioning_service.app.service import generate_positioning

router = APIRouter()


@router.post("/positioning/generate")
async def trigger_positioning(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    profile = await generate_positioning(company_id, tenant_id, db)
    return {"status": "completed", "profile": profile.model_dump()}


@router.get("/positioning/{company_id}")
async def get_positioning(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("SELECT * FROM positioning_profiles WHERE company_id=:cid AND is_current=true LIMIT 1"),
        {"cid": str(company_id)},
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Positioning profile not found")
    return dict(row)


@router.put("/positioning/{company_id}/approve")
async def approve_positioning(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await db.execute(
        text("""
            UPDATE positioning_profiles
            SET is_approved = true, approved_at = NOW()
            WHERE company_id = :cid AND is_current = true
        """),
        {"cid": str(company_id)},
    )
    await db.commit()
    return {"status": "approved"}
