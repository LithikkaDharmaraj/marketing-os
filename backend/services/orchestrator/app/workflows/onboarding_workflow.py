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
    from services.orchestrator.app.activities.intelligence_activity import ExtractIntelligenceActivity
    from services.orchestrator.app.activities.positioning_activity import GeneratePositioningActivity
    from services.orchestrator.app.activities.icp_activity import GenerateICPActivity
    from services.orchestrator.app.activities.embedding_activity import EmbedProfilesActivity
    from services.orchestrator.app.activities.notification_activity import PublishProgressActivity

RETRY_POLICY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=2),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=30),
)

ACTIVITY_TIMEOUT = timedelta(minutes=10)

_OPTS = {
    "schedule_to_close_timeout": ACTIVITY_TIMEOUT,
    "retry_policy": RETRY_POLICY,
}


@workflow.defn
class BusinessOnboardingWorkflow:
    """Master workflow: Intake → Scraping → Intelligence → Positioning → ICP → Embedding → Done"""

    @workflow.run
    async def run(self, params: dict) -> dict:
        company_id = params["company_id"]
        tenant_id = params["tenant_id"]
        run_id = params["workflow_run_id"]
        website_url = params["website_url"]
        linkedin_url = params.get("linkedin_url")
        competitors = params.get("competitors", [])

        async def notify(step: str, step_num: int, msg: str = ""):
            await workflow.execute_activity(
                PublishProgressActivity.run,
                args=[{"run_id": run_id, "step": step, "steps_done": step_num, "message": msg}],
                **_OPTS,
            )

        try:
            # Step 1: Scraping (parallel fan-out)
            await notify("scraping", 1)
            scrape_tasks = [
                workflow.execute_activity(
                    ScrapeWebsiteActivity.run,
                    args=[{"company_id": company_id, "tenant_id": tenant_id, "website_url": website_url}],
                    **_OPTS,
                ),
                workflow.execute_activity(
                    ScrapePublicSignalsActivity.run,
                    args=[{"company_id": company_id, "tenant_id": tenant_id}],
                    **_OPTS,
                ),
                workflow.execute_activity(
                    ScrapeCrunchbaseActivity.run,
                    args=[{"company_id": company_id, "tenant_id": tenant_id}],
                    **_OPTS,
                ),
            ]
            if linkedin_url:
                scrape_tasks.append(
                    workflow.execute_activity(
                        ScrapeLinkedInActivity.run,
                        args=[{"company_id": company_id, "tenant_id": tenant_id, "linkedin_url": linkedin_url}],
                        **_OPTS,
                    )
                )
            if competitors:
                scrape_tasks.append(
                    workflow.execute_activity(
                        ScrapeCompetitorsActivity.run,
                        args=[{"company_id": company_id, "tenant_id": tenant_id, "competitors": competitors}],
                        **_OPTS,
                    )
                )

            await asyncio.gather(*scrape_tasks, return_exceptions=True)

            await notify("cleaning", 2)

            # Step 3: Business Intelligence
            await notify("extracting", 3)
            await workflow.execute_activity(
                ExtractIntelligenceActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **_OPTS,
            )

            # Step 4: Positioning
            await notify("positioning", 4)
            await workflow.execute_activity(
                GeneratePositioningActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **_OPTS,
            )

            # Step 5: ICP Generation
            await notify("icp_generating", 5)
            await workflow.execute_activity(
                GenerateICPActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **_OPTS,
            )

            # Step 6: Embedding
            await notify("embedding", 6)
            await workflow.execute_activity(
                EmbedProfilesActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **_OPTS,
            )

            await notify("completed", 8, "Marketing blueprint ready")
            return {"status": "completed", "company_id": company_id}

        except Exception as e:
            await notify("failed", 0, str(e))
            raise
