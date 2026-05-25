import uuid
import json
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from shared.models.company import Company, Contact, Product, WorkflowRun, WorkflowStatus
from shared.utils.redis_client import get_redis
from shared.config import get_settings
from services.intake_service.app.schemas import CompanyIntakeRequest

settings = get_settings()

logger = logging.getLogger(__name__)


async def create_intake(
    request: CompanyIntakeRequest,
    db: AsyncSession,
) -> tuple[Company, WorkflowRun]:
    """Persist intake data and create a workflow run record."""
    # Deduplicate: check if domain already onboarded for tenant
    domain = _extract_domain(request.website_url)
    existing = await db.execute(
        select(Company).where(
            Company.tenant_id == request.tenant_id,
            Company.domain == domain,
            Company.deleted_at.is_(None),
        )
    )
    existing_company = existing.scalar_one_or_none()
    if existing_company:
        logger.info(f"Company {domain} already exists for tenant {request.tenant_id}, re-triggering workflow")
        run_result = await db.execute(
            select(WorkflowRun)
            .where(WorkflowRun.company_id == existing_company.id)
            .order_by(WorkflowRun.created_at.desc())
            .limit(1)
        )
        existing_run = run_result.scalar_one_or_none()
        if existing_run and existing_run.status.value not in ("failed", "partial"):
            return existing_company, existing_run

        # Create a fresh run so the pipeline re-executes
        new_run = WorkflowRun(
            tenant_id=request.tenant_id,
            company_id=existing_company.id,
            workflow_type="business_onboarding",
            status=WorkflowStatus.queued,
            started_at=datetime.utcnow(),
            progress={"steps_total": 8, "steps_done": 0, "current_step": "intake", "percent": 0},
        )
        db.add(new_run)
        existing_company.intelligence_status = WorkflowStatus.queued
        await db.commit()
        await db.refresh(new_run)

        orchestrator_port = getattr(settings, "orchestrator_port", 8008)
        orchestrator_url = f"http://orchestrator:{orchestrator_port}/api/v1/workflow/start"
        workflow_payload = {
            "company_id": str(existing_company.id),
            "tenant_id": str(request.tenant_id),
            "workflow_run_id": str(new_run.id),
            "website_url": existing_company.website_url,
            "linkedin_url": existing_company.linkedin_url,
            "competitors": request.competitors,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(orchestrator_url, json=workflow_payload)
                resp.raise_for_status()
                logger.info(f"Re-triggered workflow: {resp.json()}")
        except Exception as exc:
            logger.warning(f"Could not re-trigger workflow immediately: {exc}")
            try:
                redis = await get_redis()
                await redis.lpush("intake:submissions", json.dumps(workflow_payload))
            except Exception:
                pass
        return existing_company, new_run

    # Create company
    company = Company(
        tenant_id=request.tenant_id,
        name=request.company_name,
        domain=domain,
        website_url=request.website_url,
        linkedin_url=request.linkedin_url,
        crunchbase_url=request.crunchbase_url,
        industry=request.industry,
        sub_industry=request.sub_industry,
        business_model=request.business_model,
        company_size=request.company_size,
        geography=request.geography,
        pricing_range=request.pricing_range,
        annual_revenue_range=request.annual_revenue_range,
        intelligence_status=WorkflowStatus.queued,
        intake_data=request.model_dump(mode="json", exclude={"contacts", "tenant_id"}),
    )
    db.add(company)
    await db.flush()

    # Create contacts
    for c in request.contacts:
        contact = Contact(
            tenant_id=request.tenant_id,
            company_id=company.id,
            full_name=c.full_name,
            email=c.email,
            phone=c.phone,
            linkedin_url=c.linkedin_url,
            job_title=c.job_title,
            contact_type=c.contact_type,
            is_founder=c.is_founder,
            is_primary=c.is_primary,
        )
        db.add(contact)

    # Create product
    product = Product(
        tenant_id=request.tenant_id,
        company_id=company.id,
        name=request.product_name or request.company_name,
        description=request.product_description or request.services_products,
        product_type=request.product_type,
        pricing_range=request.pricing_range,
        core_features=request.core_features,
        differentiators=request.differentiators,
        problems_solved=request.problems_solved,
        target_market=request.target_market,
        goals=request.goals,
        raw_intake=request.model_dump(mode="json"),
    )
    db.add(product)

    # Create workflow run
    run = WorkflowRun(
        tenant_id=request.tenant_id,
        company_id=company.id,
        workflow_type="business_onboarding",
        status=WorkflowStatus.queued,
        started_at=datetime.utcnow(),
        progress={
            "steps_total": 8,
            "steps_done": 0,
            "current_step": "intake",
            "percent": 0,
        },
    )
    db.add(run)
    await db.flush()

    # Update company with run id
    company.workflow_run_id = run.id

    await db.commit()

    # Trigger the Temporal workflow via orchestrator service
    orchestrator_port = getattr(settings, "orchestrator_port", 8008)
    orchestrator_url = f"http://orchestrator:{orchestrator_port}/api/v1/workflow/start"
    workflow_payload = {
        "company_id": str(company.id),
        "tenant_id": str(request.tenant_id),
        "website_url": request.website_url,
        "linkedin_url": request.linkedin_url,
        "competitors": request.competitors,
        "workflow_run_id": str(run.id),
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(orchestrator_url, json=workflow_payload)
            resp.raise_for_status()
            logger.info(f"Workflow started: {resp.json()}")
    except Exception as exc:
        # Non-fatal: the run record exists, the workflow can be retried
        logger.warning(f"Could not trigger workflow immediately (will retry): {exc}")
        # Fallback: push to Redis so the orchestrator can pick it up
        try:
            redis = await get_redis()
            await redis.lpush("intake:submissions", json.dumps(workflow_payload))
        except Exception:
            pass

    logger.info(f"Intake created: company={company.id}, run={run.id}")
    return company, run


def _extract_domain(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    return domain.replace("www.", "").lower()
