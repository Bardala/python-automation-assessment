# API Reference

The API provides two primary endpoints for asynchronous task management.

## Endpoints

### 1. Submit Solving Task
`POST /recaptcha/in`

Submits a new URL for reCAPTCHA solving.

**Request Body:**
```json
{
  "url": "string"
}
```

**Response (202 Accepted):**
```json
{
  "task_id": "uuid-string",
  "status": "QUEUED"
}
```

---

### 2. Get Task Result
`GET /recaptcha/res/{task_id}`

Retrieves the current status and result of a specific task.

**Response (200 OK):**
```json
{
  "task_id": "uuid-string",
  "status": "COMPLETED",
  "result": {
    "score": 0.9,
    "token": "...",
    "action": "homepage"
  },
  "error": null
}
```

## Data Models

### Job Statuses
- `QUEUED`: Task is in line for processing.
- `PROCESSING`: Worker is currently automating the browser for this task.
- `COMPLETED`: Solving successful; results are available in the `result` field.
- `FAILED`: Solving failed or timed out; details are in the `error` field.

## Error Handling
- **404 Not Found**: If the `task_id` does not exist in the store.
- **500 Internal Server Error**: Unexpected system failures (errors during solving are captured within the job status, not the HTTP response).
