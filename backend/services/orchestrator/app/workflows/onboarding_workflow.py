import asyncio
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from services.orchestrator.app.activities.scraping_activities import ScrapeWebsiteActivity
    from services.orchestrator.app.activities.intelligence_activity import ExtractIntelligenceActivity
    from services.orchestrator.app.activities.positioning_activity import GeneratePositioningActivity
    from services.orchestrator.app.activities.icp_activity import GenerateICPActivity
    from services.orchestrator.app.activities.embedding_activity import EmbedProfilesActivity
    from services.orchestrator.app.activities.notification_activity import PublishProgressActivity
    from services.orchestrator.app.activities.target_discovery_activity import DiscoverTargetsActivity

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
            # Step 1: Scraping — one comprehensive call handles website + LinkedIn + competitors + signals
            await notify("scraping", 1)
            await workflow.execute_activity(
                ScrapeWebsiteActivity.run,
                args=[{
                    "company_id": company_id,
                    "tenant_id": tenant_id,
                    "website_url": website_url,
                    "linkedin_url": linkedin_url,
                    "competitors": competitors,
                    "company_name": params.get("company_name", ""),
                    "industry": params.get("industry", ""),
                    "domain": params.get("domain", ""),
                }],
                **_OPTS,
            )

            await notify("cleaning", 2)

            # Step 3: Business Intelligence (extracts product intelligence too)
            await notify("extracting", 3)
            await workflow.execute_activity(
                ExtractIntelligenceActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **_OPTS,
            )

            # Step 4: Positioning (uses product intelligence)
            await notify("positioning", 4)
            await workflow.execute_activity(
                GeneratePositioningActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **_OPTS,
            )

            # Step 5: ICP Generation (uses product intelligence + positioning)
            await notify("icp_generating", 5)
            await workflow.execute_activity(
                GenerateICPActivity.run,
                args=[{"company_id": company_id, "tenant_id": tenant_id}],
                **_OPTS,
            )

            # Steps 6 + 7: Target Discovery and Embedding run in PARALLEL
            # — both depend on ICP/positioning but not on each other
            await notify("target_discovering", 6)
            await asyncio.gather(
                workflow.execute_activity(
                    DiscoverTargetsActivity.run,
                    args=[{"company_id": company_id, "tenant_id": tenant_id}],
                    **_OPTS,
                ),
                workflow.execute_activity(
                    EmbedProfilesActivity.run,
                    args=[{"company_id": company_id, "tenant_id": tenant_id}],
                    **_OPTS,
                ),
                return_exceptions=True,
            )

            await notify("completed", 8, "Marketing blueprint ready")
            return {"status": "completed", "company_id": company_id}

        except Exception as e:
            await notify("failed", 0, str(e))
            raise
