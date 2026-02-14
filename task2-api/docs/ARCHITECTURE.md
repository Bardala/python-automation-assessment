# System Architecture

This microservice is designed as a scalable, developer-friendly API for reCAPTCHA solving, abstracting away the complexities of browser automation and stealth management.

## High-Level Design

The system follows a classic **Producer-Consumer** pattern implemented using FastAPI and Python's `asyncio`.

### Core Components

1.  **FastAPI Front-end**: Handles incoming HTTP requests. It is designed to be non-blocking, returning a `task_id` immediately upon submission.
2.  **Job Store (State Manager)**: A singleton in-memory database that tracks the lifecycle of every task (QUEUED, PROCESSING, COMPLETED, FAILED).
3.  **Task Queue**: An internal `asyncio.Queue` that manages the backlog of pending work.
4.  **Background Worker**: A persistent loop that consumes tasks from the queue and executes the stealth browser logic.
5.  **Browser Manager**: A singleton that maintains a persistent browser instance, spawning isolated contexts for each task to ensure security and performance.

## Data Flow

1.  **Submission**: Client sends a POST request to `/recaptcha/in`.
2.  **Queueing**: The API creates a `Job` record, pushes the `task_id` to the queue, and returns the ID to the client.
3.  **Processing**: The Background Worker picks up the task, creates a new browser context, and executes the reCAPTCHA solving logic (imported from Task 1).
4.  **Update**: Once complete, the worker updates the `Job` record with the result (token, score) or error message.
5.  **Retrieval**: The client polls `/recaptcha/res/{task_id}` to fetch the result.

## Component Map

- `src/main.py`: Application entry point and lifespan management.
- `src/api/`: Request handling and data validation.
- `src/core/state.py`: Global state and persistence simulation.
- `src/core/worker.py`: Automation execution and browser lifecycle.
