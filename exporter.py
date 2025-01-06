import os
import time
import requests
import logging
from prometheus_client import start_http_server, Gauge
from dotenv import load_dotenv  # Add this import to load the .env file

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Environment Variables
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
SCRAPE_INTERVAL = int(os.getenv("SCRAPE_INTERVAL", 15))

# Prometheus Metrics
METRICS = {
    "messages": Gauge(
        "rabbitmq_individual_queue_messages",
        "Total messages in queue",
        ["host", "vhost", "name"],
    ),
    "messages_ready": Gauge(
        "rabbitmq_individual_queue_messages_ready",
        "Ready messages in queue",
        ["host", "vhost", "name"],
    ),
    "messages_unacknowledged": Gauge(
        "rabbitmq_individual_queue_messages_unacknowledged",
        "Unacknowledged messages in queue",
        ["host", "vhost", "name"],
    ),
}

def fetch_queue_data():
    """Fetch queue data from RabbitMQ Management API with retry logic."""
    url = f"http://{RABBITMQ_HOST}:15672/api/queues"
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, auth=(RABBITMQ_USER, RABBITMQ_PASSWORD), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    logging.error("Failed to fetch RabbitMQ data after multiple attempts.")
    return []

def clean_stale_metrics(existing_queues):
    """Remove metrics for queues that no longer exist."""
    existing_keys = {(queue['name'], queue['vhost']) for queue in existing_queues}
    for labels in METRICS["messages"]._metrics.keys():
        queue_name, vhost = labels[1], labels[2]
        if (queue_name, vhost) not in existing_keys:
            for metric in METRICS.values():
                metric.remove(*labels)

def update_metrics():
    """Update Prometheus metrics with RabbitMQ queue data."""
    queues = fetch_queue_data()
    if not queues:
        return

    for queue in queues:
        vhost = queue["vhost"]
        name = queue["name"]
        host = RABBITMQ_HOST

        try:
            METRICS["messages"].labels(host=host, vhost=vhost, name=name).set(
                queue.get("messages", 0)
            )
            METRICS["messages_ready"].labels(host=host, vhost=vhost, name=name).set(
                queue.get("messages_ready", 0)
            )
            METRICS["messages_unacknowledged"].labels(
                host=host, vhost=vhost, name=name
            ).set(queue.get("messages_unacknowledged", 0))
        except Exception as e:
            logging.warning(f"Failed to update metrics for queue {name}: {e}")

    clean_stale_metrics(queues)

if __name__ == "__main__":
    # Start Prometheus HTTP Server
    start_http_server(8000)
    logging.info("Prometheus exporter running on port 8000...")
    while True:
        update_metrics()
        time.sleep(SCRAPE_INTERVAL)
