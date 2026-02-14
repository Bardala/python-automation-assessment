# Task 2: Python API Framework Assessment

This project implements a **FastAPI** microservice that wraps the reCAPTCHA v3 automation (from Task 1) into a robust, queue-based architecture. It mimics a distributed system design (Task 4) using local in-memory components.

## 🚀 Features

*   **Async API**: Built with FastAPI for high-performance asynchronous request handling.
*   **Job Queue Architecture**: Decouples request ingestion from heavy browser processing.
*   **Background Worker**: A dedicated worker loop that consumes tasks and manages the Playwright browser lifecycle.
*   **Polling Simulation**: Includes a full-cycle client script (`simulation.py`) that mimics a real customer interaction.
*   **System Design Ready**: Structured to easily scale by replacing in-memory queues with RabbitMQ/Redis.

## 📂 Project Structure

```text
task2-api/
├── src/
│   ├── api/
│   │   ├── routes.py       # Endpoint logic (/recaptcha/in, /recaptcha/res)
│   │   └── models.py       # Pydantic data schemas
│   ├── core/
│   │   ├── state.py        # In-memory JobStore & Queue (Mocking DB & RabbitMQ)
│   │   └── worker.py       # Background consumer bridging to Task 1
│   └── main.py             # App entry point
├── simulation.py           # Client script for end-to-end testing
└── README.md               # This file
```

## 🛠️ Setup & Installation

**Prerequisites:**
*   Python 3.10+
*   The `task1-recaptcha-stealth` directory must be a sibling to `task2-api`.

1.  **Create Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn requests playwright playwright-stealth
    playwright install chromium
    ```

## 🏃‍♂️ Usage

### 1. Start the API Server
Run the helper script from the `task2-api` directory:

```bash
./start_server.sh
```

Or manually:
```bash
# We set PYTHONPATH to include 'src' and the parent directory so Task 1 modules resolve correctly
PYTHONPATH=src:../task1-recaptcha-stealth .venv/bin/uvicorn main:app --port 8000 --reload
```

You should see logs indicating the Worker has started:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000
👷 Worker: Started background loop...
👷 Worker: Browser Interface Ready.
```

### 2. Run the Customer Simulation
Open a new terminal and run the client script:

```bash
source .venv/bin/activate
python simulation.py
```

**Expected Output:**
```text
🚀 [Customer] Starting simulation request...
📥 [Customer] Task Submitted. ID: 539c8f27...
⏳ [Customer] Status: PROCESSING (Elapsed: 2.0s)
...
✅ [Customer] SUCCESS!
   Score: 0.9
   Token: 03AFcWeA...
```

## 🧩 API Reference

### Submit Task
*   **Endpoint:** `POST /recaptcha/in`
*   **Body:** `{"url": "https://target-site.com"}`
*   **Response:** `{"task_id": "uuid", "status": "QUEUED"}`

### Get Result
*   **Endpoint:** `GET /recaptcha/res/{task_id}`
*   **Response:**
    *   `{"status": "PROCESSING", ...}`
    *   `{"status": "COMPLETED", "result": {"score": 0.9, "token": "..."}, ...}`

## 🏗️ Architecture Notes (Task 4 Context)
This implementation serves as the **MVP** for the System Design in Task 4.
*   **Current State**: Uses `asyncio.Queue` and In-Memory Dict.
*   **Production Path**:
    *   Replace `asyncio.Queue` with `aio_pika` (RabbitMQ).
    *   Replace `JobStore` with `SQLAlchemy` (PostgreSQL).
    *   Deploy API and Workers as separate Docker containers.
