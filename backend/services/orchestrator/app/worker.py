import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner
from shared.config import get_settings
from services.orchestrator.app.workflows.onboarding_workflow import BusinessOnboardingWorkflow
from services.orchestrator.app.workflows.scraping_workflow import ScrapingWorkflow
from services.orchestrator.app.activities.intake_activity import intake_activity
from services.orchestrator.app.activities.scraping_activities import (
    ScrapeWebsiteActivity, ScrapeLinkedInActivity,
    ScrapeCrunchbaseActivity, ScrapeCompetitorsActivity, ScrapePublicSignalsActivity,
)
from services.orchestrator.app.activities.intelligence_activity import ExtractIntelligenceActivity
from services.orchestrator.app.activities.positioning_activity import GeneratePositioningActivity
from services.orchestrator.app.activities.icp_activity import GenerateICPActivity
from services.orchestrator.app.activities.embedding_activity import EmbedProfilesActivity
from services.orchestrator.app.activities.notification_activity import PublishProgressActivity
from services.orchestrator.app.activities.target_discovery_activity import DiscoverTargetsActivity

logger = logging.getLogger(__name__)
settings = get_settings()


async def main():
    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)

    worker = Worker(
        client,
        task_queue="marketing-os-main",
        workflows=[BusinessOnboardingWorkflow, ScrapingWorkflow],
        workflow_runner=UnsandboxedWorkflowRunner(),
        activities=[
            intake_activity,
            ScrapeWebsiteActivity().run,
            ScrapeLinkedInActivity().run,
            ScrapeCrunchbaseActivity().run,
            ScrapeCompetitorsActivity().run,
            ScrapePublicSignalsActivity().run,
            ExtractIntelligenceActivity().run,
            GeneratePositioningActivity().run,
            GenerateICPActivity().run,
            EmbedProfilesActivity().run,
            PublishProgressActivity().run,
            DiscoverTargetsActivity().run,
        ],
    )

    logger.info("Temporal worker started on queue: marketing-os-main")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
