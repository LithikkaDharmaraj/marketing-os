import uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.utils.db import get_db
from shared.models.company import ScrapedPage, WorkflowRun
from services.scraper_service.app.service import run_full_scrape

router = APIRouter()


class ScrapeRequest(BaseModel):
    company_id: uuid.UUID
    tenant_id: uuid.UUID
    website_url: str
    linkedin_url: str | None = None
    competitors: list[str] = []
    company_name: str = ""
    industry: str = ""
    domain: str = ""


@router.post("/scrape/company")
async def scrape_company(request: ScrapeRequest, db: AsyncSession = Depends(get_db)):
    results = await run_full_scrape(
        company_id=request.company_id,
        tenant_id=request.tenant_id,
        db=db,
        website_url=request.website_url,
        linkedin_url=request.linkedin_url,
        competitors=request.competitors,
        company_name=request.company_name,
        industry=request.industry,
        domain=request.domain,
    )
    return {"status": "completed", "sources_scraped": list(results.keys())}


@router.get("/scrape/results/{company_id}")
async def get_scrape_results(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScrapedPage).where(ScrapedPage.company_id == company_id)
    )
    pages = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "source_type": p.source_type,
            "source_url": p.source_url,
            "status": p.status.value,
            "scraped_at": p.scraped_at.isoformat() if p.scraped_at else None,
        }
        for p in pages
    ]
