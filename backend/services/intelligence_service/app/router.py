import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.utils.db import get_db
from shared.models.company import Company, WorkflowRun
from services.intelligence_service.app.service import extract_business_intelligence

router = APIRouter()


@router.post("/intelligence/extract")
async def trigger_extraction(
    company_id: uuid.UUID,
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    profile = await extract_business_intelligence(company_id, tenant_id, db)
    return {"status": "completed", "profile": profile.model_dump()}


@router.get("/intelligence/{company_id}")
async def get_intelligence(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    enriched = company.enriched_data or {}

    # Fetch latest workflow run to expose stuck-state to frontend
    run_result = await db.execute(
        select(WorkflowRun)
        .where(WorkflowRun.company_id == company.id)
        .order_by(WorkflowRun.created_at.desc())
        .limit(1)
    )
    latest_run = run_result.scalars().first()

    # Support both new keys and legacy key for backward compat
    ai_discovered = enriched.get("ai_discovered_competitors") or enriched.get("competitor_profiles", [])
    user_suggested = enriched.get("user_suggested_competitors", [])

    return {
        "company_id": str(company.id),
        "company_name": company.name,
        "industry": company.industry,
        "business_model": company.business_model,
        "status": company.intelligence_status.value,
        "workflow_run_status": latest_run.status if latest_run else None,
        "business_profile": enriched.get("business_profile"),
        "ai_discovered_competitors": ai_discovered,
        "user_suggested_competitors": user_suggested,
        "competitor_profiles": ai_discovered,
    }


@router.get("/intelligence/{company_id}/competitors")
async def get_competitors(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from shared.models.company import ScrapedPage
    result = await db.execute(
        select(ScrapedPage).where(
            ScrapedPage.company_id == company_id,
            ScrapedPage.source_type == "competitor",
        )
    )
    pages = result.scalars().all()
    return [
        {"url": p.source_url, "data": p.structured_data, "scraped_at": p.scraped_at}
        for p in pages
    ]
