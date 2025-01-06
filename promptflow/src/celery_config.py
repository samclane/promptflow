# Configuration for the Celery instance
import os

import dotenv

dotenv.load_dotenv()

broker_url = os.getenv(
    "REDIS_URL", "redis://localhost:6379/0"
)  # The URL of the message broker (Redis in this case)
result_backend = os.getenv(
    "REDIS_URL", "redis://localhost:6379/0"
)  # Optional: Using Redis to store task results
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True
