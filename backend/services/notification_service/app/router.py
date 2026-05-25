from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.notification_service.app.sse_manager import event_stream

router = APIRouter()


@router.get("/events/{workflow_run_id}")
async def workflow_events(workflow_run_id: str):
    """Server-Sent Events endpoint — stream real-time workflow progress to frontend."""
    return StreamingResponse(
        event_stream(workflow_run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
