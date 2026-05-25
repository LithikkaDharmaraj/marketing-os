import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.utils.db import get_db
from shared.models.company import Company, WorkflowRun
from services.intake_service.app.schemas import (
    CompanyIntakeRequest,
    CompanyIntakeResponse,
    IntakeStatusResponse,
)
from services.intake_service.app.service import create_intake

router = APIRouter()


@router.post("/intake", response_model=CompanyIntakeResponse, status_code=status.HTTP_201_CREATED)
async def submit_intake(
    request: CompanyIntakeRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit business intake form — triggers the full onboarding workflow."""
    company, run = await create_intake(request, db)
    return CompanyIntakeResponse(
        company_id=company.id,
        workflow_run_id=run.id,
        status=company.intelligence_status.value,
        message="Intake received. Processing started.",
    )


@router.get("/intake/{company_id}", response_model=IntakeStatusResponse)
async def get_intake_status(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    run_result = await db.execute(
        select(WorkflowRun)
        .where(WorkflowRun.company_id == company_id)
        .order_by(WorkflowRun.created_at.desc())
    )
    run = run_result.scalar_one_or_none()

    return IntakeStatusResponse(
        company_id=company.id,
        workflow_run_id=run.id if run else uuid.uuid4(),
        status=company.intelligence_status.value,
        progress=run.progress if run else {},
        company_name=company.name,
    )


@router.patch("/intake/{company_id}")
async def update_intake(
    company_id: uuid.UUID,
    updates: dict,
    db: AsyncSession = Depends(get_db),
):
    """Allow editing intake fields before processing completes."""
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.intelligence_status.value not in ("queued", "pending"):
        raise HTTPException(status_code=409, detail="Cannot edit: processing already started")

    allowed_fields = {"industry", "sub_industry", "company_size", "geography", "business_model", "pricing_range"}
    for field, value in updates.items():
        if field in allowed_fields and hasattr(company, field):
            setattr(company, field, value)

    await db.commit()
    return {"status": "updated", "company_id": str(company_id)}
