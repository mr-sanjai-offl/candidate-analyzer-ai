"""Celery application configuration.

Sets up the Celery application with Redis broker, queues, routing,
and worker parameters for the background processing engine.
"""

from celery import Celery
from kombu import Exchange, Queue

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "apexguidance_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

# Setup task queues (analysis, collector, report, default)
celery_app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("analysis", Exchange("analysis"), routing_key="analysis.#"),
    Queue("collector", Exchange("collector"), routing_key="collector.#"),
    Queue("report", Exchange("report"), routing_key="report.#"),
)

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"

# Task routing
celery_app.conf.task_routes = {
    "app.tasks.analysis.*": {"queue": "analysis"},
    "app.tasks.collectors.*": {"queue": "collector"},
    "app.tasks.reports.*": {"queue": "report"},
}

# Production configurations
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Worker health and timeouts
    worker_prefetch_multiplier=1, # Fair distribution for long running tasks
    task_acks_late=True, # Acknowledge task only after completion
    task_reject_on_worker_lost=True, # Requeue on worker crash
    result_expires=86400, # 1 day expiration for results
    task_track_started=True,
    # Dead letter / retry policy
    task_publish_retry=True,
    task_publish_retry_policy={
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.5,
    },
)

# Auto-discover tasks from the tasks module
celery_app.autodiscover_tasks(["app.tasks"])
