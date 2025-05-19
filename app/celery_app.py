"""
Celery application configuration for RobustRepo v2.0
"""
from celery import Celery
from .config import Config

def create_celery_app():
    """Create and configure Celery application with Redis backend"""
    app = Celery(
        'robusterepo',
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['app.tasks']
    )
    
    # Configure Celery
    app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        result_expires=3600,  # Results expire after 1 hour
        task_acks_late=True,  # Tasks acknowledged after completion
        task_reject_on_worker_lost=True,  # Reject tasks if worker dies
        task_track_started=True,  # Track when tasks start
        task_send_sent_event=True,  # Send task-sent events for monitoring
        worker_prefetch_multiplier=1,  # Disable prefetching for better task distribution
        worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks to prevent memory leaks
        beat_schedule={},  # No scheduled tasks for now
        task_routes={
            'app.tasks.process_repository_task': {'queue': 'default'},
        },
        task_annotations={
            'app.tasks.process_repository_task': {
                'rate_limit': '10/m',  # Max 10 repository processing tasks per minute
                'time_limit': 300,     # 5 minute hard time limit
                'soft_time_limit': 240  # 4 minute soft time limit
            }
        }
    )
    
    return app

# Create the Celery app instance
celery_app = create_celery_app()