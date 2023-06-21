from celery import Celery

# Create a Celery instance
celery_app = Celery("promptflow")

# Load configuration
celery_app.config_from_object("promptflow.src.celery_config")
