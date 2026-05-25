import asyncio
import json
import logging
from typing import AsyncGenerator
from shared.utils.redis_client import get_redis

logger = logging.getLogger(__name__)

WORKFLOW_STEPS = [
    "intake", "scraping", "cleaning", "extracting",
    "positioning", "icp_generating", "embedding", "completed",
]

STEP_LABELS = {
    "intake": "Processing intake",
    "scraping": "Scraping web & social data",
    "cleaning": "Cleaning & normalizing data",
    "extracting": "AI business intelligence extraction",
    "positioning": "Generating positioning strategy",
    "icp_generating": "Building ICP profiles",
    "embedding": "Storing in vector memory",
    "completed": "Marketing blueprint ready",
    "failed": "Processing failed",
}


async def event_stream(workflow_run_id: str) -> AsyncGenerator[str, None]:
    """SSE generator — subscribes to Redis pub/sub channel for a workflow run."""
    redis = await get_redis()
    channel = f"workflow:progress:{workflow_run_id}"

    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)

    try:
        yield _format_event({"type": "connected", "run_id": workflow_run_id})

        deadline = asyncio.get_event_loop().time() + 620
        last_heartbeat = asyncio.get_event_loop().time()

        while True:
            now = asyncio.get_event_loop().time()
            if now >= deadline:
                yield _format_event({"type": "timeout", "message": "Processing timeout"})
                break

            # Send a comment heartbeat every 25s so nginx/proxies don't time out
            if now - last_heartbeat >= 25:
                yield ": heartbeat\n\n"
                last_heartbeat = now

            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    yield _format_event(data)
                    if data.get("step") in ("completed", "failed"):
                        break
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Malformed SSE event: {e}")
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()


async def publish_progress(
    workflow_run_id: str,
    step: str,
    steps_done: int,
    steps_total: int = 8,
    message: str = "",
    error: str | None = None,
) -> None:
    """Publish a progress event to Redis pub/sub and update DB status."""
    redis = await get_redis()
    percent = int((steps_done / steps_total) * 100)
    payload = {
        "type": "progress",
        "run_id": workflow_run_id,
        "step": step,
        "step_label": STEP_LABELS.get(step, step),
        "steps_done": steps_done,
        "steps_total": steps_total,
        "percent": percent,
        "message": message or STEP_LABELS.get(step, ""),
        "error": error,
    }
    channel = f"workflow:progress:{workflow_run_id}"
    await redis.publish(channel, json.dumps(payload))

    # Also update workflow_runs table
    VALID_STATUSES = {"pending", "queued", "scraping", "cleaning", "extracting",
                      "positioning", "icp_generating", "embedding", "completed", "failed", "partial"}
    db_status = step if step in VALID_STATUSES else "scraping"
    try:
        from shared.utils.db import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as db:
            await db.execute(
                text("""
                    UPDATE workflow_runs
                    SET status = CAST(:status AS workflow_status),
                        progress = CAST(:progress AS jsonb),
                        completed_at = CASE WHEN :status IN ('completed','failed') THEN NOW() ELSE completed_at END,
                        updated_at = NOW()
                    WHERE id = CAST(:run_id AS UUID)
                """),
                {
                    "status": db_status,
                    "progress": json.dumps({"steps_total": steps_total, "steps_done": steps_done, "current_step": step, "percent": percent}),
                    "run_id": workflow_run_id,
                },
            )
            await db.commit()
    except Exception as e:
        logger.warning(f"Could not update workflow_runs status: {e}")


def _format_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"
