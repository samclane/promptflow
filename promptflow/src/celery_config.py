# Configuration for the Celery instance
broker_url = (
    "amqp://localhost//"  # The URL of the message broker (RabbitMQ in this case)
)
result_backend = "rpc://"  # Optional: Using RabbitMQ to store task results
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True
