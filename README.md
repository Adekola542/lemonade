# RabbitMQ Prometheus Exporter

## Overview
This is a Prometheus exporter for RabbitMQ that connects to the RabbitMQ Management API and periodically fetches metrics for all queues in all vhosts. The exported metrics include:
- Total messages in the queue
- Messages ready for delivery
- Messages unacknowledged

## Features
- Configurable using environment variables
- Automatically removes stale metrics when queues are deleted
- Includes retry logic for API calls with exponential backoff
- Designed for deployment using Docker

## Metrics
The following metrics are exported:
- `rabbitmq_individual_queue_messages{host, vhost, name}`
- `rabbitmq_individual_queue_messages_ready{host, vhost, name}`
- `rabbitmq_individual_queue_messages_unacknowledged{host, vhost, name}`

## Environment Variables
- `RABBITMQ_HOST`: RabbitMQ hostname (default: `localhost`)
- `RABBITMQ_USER`: RabbitMQ username (default: `guest`)
- `RABBITMQ_PASSWORD`: RabbitMQ password (default: `guest`)
- `SCRAPE_INTERVAL`: Interval (in seconds) to scrape metrics (default: `15`)

## Usage

### Running Locally
1. Install dependencies: `pip install prometheus-client requests`
2. Set the required environment variables.
3. Run the script: `python exporter.py`

### Running with Docker
1. Build the Docker image:
   ```bash
   docker build -t rabbitmq-exporter .
