import uuid
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from temporalio.client import Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from shared.config import get_settings
from shared.utils.db import get_db
from shared.models.company import WorkflowRun

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()

_temporal_client: Client | None = None


async def get_temporal_client() -> Client:
    global _temporal_client
    if _temporal_client is None:
        _temporal_client = await Client.connect(settings.temporal_host)
    return _temporal_client


class WorkflowStartRequest(BaseModel):
    company_id: uuid.UUID
    tenant_id: uuid.UUID
    website_url: str
    linkedin_url: str | None = None
    competitors: list[str] = []
    workflow_run_id: uuid.UUID | None = None


@router.post("/workflow/start")
async def start_workflow(
    request: WorkflowStartRequest,
    db: AsyncSession = Depends(get_db),
):
    client = await get_temporal_client()

    run_id = request.workflow_run_id or uuid.uuid4()
    workflow_id = f"onboarding-{request.company_id}"

    try:
        handle = await client.start_workflow(
            "BusinessOnboardingWorkflow",
            args=[{
                "company_id": str(request.company_id),
                "tenant_id": str(request.tenant_id),
                "workflow_run_id": str(run_id),
                "website_url": request.website_url,
                "linkedin_url": request.linkedin_url,
                "competitors": request.competitors,
            }],
            id=workflow_id,
            task_queue="marketing-os-main",
        )

        # Update DB with temporal run id
        await db.execute(
            text("""
                UPDATE workflow_runs SET temporal_run_id = :tid, status = 'queued'
                WHERE id = :rid
            """),
            {"tid": handle.id, "rid": str(run_id)},
        )
        await db.commit()

        return {"workflow_id": handle.id, "run_id": str(run_id), "status": "started"}

    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/{workflow_run_id}")
async def get_workflow_status(workflow_run_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.id == workflow_run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return {
        "id": str(run.id),
        "status": run.status.value,
        "progress": run.progress,
        "temporal_run_id": run.temporal_run_id,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }
