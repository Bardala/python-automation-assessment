# Stealth Scraping API (Task 2)

A production-ready microservice framework for reCAPTCHA v3 solving, built with FastAPI and Playwright. This project demonstrates a scalable, queue-based architecture for handling heavy browser automation tasks.

## 🚀 Key Features

- **Asynchronous Processing**: Immediate task submission with delayed execution.
- **Stealth Architecture**: Integrated with advanced browser fingerprints and stealth plugins from Task 1.
- **Worker-Queue Pattern**: Decoupled request handling from resource-intensive browser operations.
- **Isolated Contexts**: Every request runs in a fresh browser context to prevent data leakage.

## 📂 Documentation

For detailed technical information, please refer to the following guides:

- **[Architecture Overview](./docs/ARCHITECTURE.md)**: System design, data flow, and component breakdown.
- **[API Reference](./docs/API_REFERENCE.md)**: Detailed endpoint documentation and data models.
- **[Worker Logic](./docs/WORKER_LOGIC.md)**: Deep dive into concurrency, browser management, and integration.
- **[Setup & Usage](./docs/SETUP_USAGE.md)**: Step-by-step instructions to get the service running.

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Start the server
./start_server.sh

# 3. In another terminal, run simulation
python simulation.py
```

## 🏗️ System Evolution

This service is designed for horizontal scalability. Transitioning to a production-grade distributed system involves:
1. Replacing the in-memory queue with **RabbitMQ** (using `aio-pika`).
2. Swapping the `JobStore` for **Redis** or **PostgreSQL**.
3. Containerizing API nodes and Worker nodes separately.
