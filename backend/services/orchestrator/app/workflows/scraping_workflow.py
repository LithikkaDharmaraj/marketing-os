"""Sub-workflow: fans out all Apify scraping actors in parallel."""
import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from services.orchestrator.app.activities.scraping_activities import (
        ScrapeWebsiteActivity,
        ScrapeLinkedInActivity,
        ScrapeCrunchbaseActivity,
        ScrapeCompetitorsActivity,
        ScrapePublicSignalsActivity,
    )

_RETRY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=2),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
)
_TIMEOUT = timedelta(minutes=5)


@workflow.defn
class ScrapingWorkflow:
    """Fan-out all scraping activities for a company in parallel."""

    @workflow.run
    async def run(self, params: dict) -> dict:
        company_id = params["company_id"]
        tenant_id = params["tenant_id"]
        website_url = params.get("website_url", "")
        linkedin_url = params.get("linkedin_url")
        competitors = params.get("competitors", [])

        def opts(timeout: timedelta = _TIMEOUT):
            return {"schedule_to_close_timeout": timeout, "retry_policy": _RETRY}

        tasks = [
            workflow.execute_activity(
                ScrapeWebsiteActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id, "website_url": website_url}],
                **opts(),
            ),
            workflow.execute_activity(
                ScrapePublicSignalsActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **opts(),
            ),
        ]

        if linkedin_url:
            tasks.append(
                workflow.execute_activity(
                    ScrapeLinkedInActivity.run,
                    args=[{"company_id": company_id, "tenant_id": tenant_id, "linkedin_url": linkedin_url}],
                    **opts(),
                )
            )

        tasks.append(
            workflow.execute_activity(
                ScrapeCrunchbaseActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **opts(),
            )
        )

        if competitors:
            tasks.append(
                workflow.execute_activity(
                    ScrapeCompetitorsActivity.run,
                    args=[{"company_id": company_id, "tenant_id": tenant_id, "competitors": competitors}],
                    **opts(timedelta(minutes=8)),
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        sources_done = sum(1 for r in results if not isinstance(r, Exception))
        sources_failed = [str(r) for r in results if isinstance(r, Exception)]

        return {
            "sources_done": sources_done,
            "sources_failed_count": len(sources_failed),
            "errors": sources_failed,
        }
