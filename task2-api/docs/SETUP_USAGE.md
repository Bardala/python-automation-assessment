# Setup & Usage Guide

## Environment Setup

1.  **Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Dependencies**:
    Install requirements and Playwright binaries:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

## Running the Server

Start the API service using the provided helper script or Uvicorn directly:

```bash
./start_server.sh
# OR
python src/main.py
```

The API will be available at `http://localhost:8000`.

## Testing the API

### Automated Simulation
Use the `simulation.py` script to mimic a real-world client interaction (Submission + Polling):

```bash
python simulation.py [TARGET_URL]
```

### Manual Testing (cURL)

**1. Submit Task:**
```bash
curl -X POST http://localhost:8000/recaptcha/in \
     -H "Content-Type: application/json" \
     -d '{"url": "https://recaptcha-demo.appspot.com/recaptcha-v3-request-scores.php"}'
```

**2. Check Status:**
```bash
curl http://localhost:8000/recaptcha/res/[TASK_ID]
```

## Production Considerations
- **Storage**: In a production environment, the in-memory `JobStore` should be replaced with Redis or PostgreSQL.
- **Queue**: Replace the internal `asyncio.Queue` with a robust broker like RabbitMQ or Celery for distributed processing.
