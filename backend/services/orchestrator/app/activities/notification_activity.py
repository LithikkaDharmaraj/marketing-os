from temporalio import activity
from services.notification_service.app.sse_manager import publish_progress


class PublishProgressActivity:
    @activity.defn(name="publish_progress")
    async def run(self, params: dict) -> None:
        await publish_progress(
            workflow_run_id=params["run_id"],
            step=params["step"],
            steps_done=params.get("steps_done", 0),
            message=params.get("message", ""),
            error=params.get("error"),
        )
