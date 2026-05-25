from celery import Celery
from shared.config import get_settings

settings = get_settings()

app = Celery(
    "marketing_os",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_routes={
        "services.scraper_service.app.tasks.*": {"queue": "scraper:jobs"},
        "services.intelligence_service.app.tasks.*": {"queue": "intelligence:extract"},
        "services.positioning_service.app.tasks.*": {"queue": "positioning:generate"},
        "services.icp_service.app.tasks.*": {"queue": "icp:generate"},
        "services.embedding_service.app.tasks.*": {"queue": "embedding:upsert"},
    },
    task_default_queue="default",
    broker_transport_options={
        "visibility_timeout": 3600,
        "fanout_prefix": True,
    },
)

# Dead-letter queue config
app.conf.task_queues = {
    "scraper:jobs": {
        "exchange": "scraper",
        "routing_key": "scraper.jobs",
    },
    "scraper:dlq": {
        "exchange": "scraper",
        "routing_key": "scraper.dlq",
    },
}
