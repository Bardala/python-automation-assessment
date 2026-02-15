# Python Automation & Crawling Assessment

This repository contains the complete solution for the **Python Developer (Automation & Crawling)** assessment. The project is structured into four distinct tasks, each demonstrating production-grade engineering practices, scalability, and robust error handling.

## 🚀 Executive Summary

| Task | Description | Status | Key Achievement |
| :--- | :--- | :--- | :--- |
| **Task 1** | Stealth Automation (reCAPTCHA v3) | ✅ **Completed** | Achieved consistent **0.9 Scores** (High Trust) using advanced fingerprinting & async concurrency. |
| **Task 2** | API Development | ✅ **Completed** | Scalable REST API wrapping the automation logic. |
| **Task 3** | DOM Scraping & Security | ✅ **Completed** | Successfully extracted hidden assets (Base64) vs. human-visible content. |
| **Task 4** | System Architecture | ✅ **Completed** | Designed a distributed, fault-tolerant scraping architecture (RabbitMQ + Workers). |

---

## 📂 Project Structure
```bash
.
├── task1-recaptcha-stealth/  # Async automation engine (Playwright + Stealth)
│   └── outputs/              # Contains `results_async.json` (250 runs) & fingerprints
├── task2-api/                # REST API Wrapper (FastAPI) & Simulation
├── task3-dom-scraping/       # DOM parsing & asset extraction logic
│   └── outputs/              # Contains `allimages.json` & `visible_images_only.json`
└── task4-system-diagram/     # Architecture design & diagrams
```

---

## 🛠️ Task 1: Stealth Automation & Scalability

**Goal:** Automate 250 reCAPTCHA v3 solves with >90% achieving a purely human score (0.9).

### 🔹 Implementation Highlights
*   **Asynchronous Core:** Built on `asyncio` and `playwright-async` to handle concurrent browser contexts efficiently.
*   **Advanced Stealth:** Implemented a custom fingerprint injection system (Canvas, WebGL, AudioContext noise) to bypass bot detection.
*   **Proxy Authentication Engine:** Developed a dynamic Chrome Extension generator to handle `user:pass` authenticated proxies, bypassing standard browser flag limitations.

### ⚠️ Note on Proxy Infrastructure
The solution includes a fully functional **Proxy Rotation System** (see `AsyncScaler` class) capable of handling authenticated proxies and improved stealth via IP rotation.

**Observation:** During testing, the free-tier **Webshare proxies** provided for the assessment were found to be:
1.  **Unreliable:** High latency or complete connection timeouts (verified via `curl` connectivity checks).
2.  **Flagged:** When reachable, they were identified as Data Center IPs, automatically capping reCAPTCHA scores at `0.1` or `0.3` regardless of the stealth implementation.

**Decision:** To demonstrate the *true* capability of the automation logic, the final scalability benchmarks (250 runs) were executed using a clean residential/local IP. **Result:** The system achieved a **0.9 score** on >90% of attempts, far exceeding the 15% requirement.

---

## 🔌 Task 2: API Framework

**Goal:** Expose the automation as a service.

*   **Endpoints:**
    *   `POST /recaptcha/in`: Accepts job parameters and returns a `TaskID`.
    *   `GET /recaptcha/res`: Polling endpoint to retrieve tokens.
*   **Simulation:** Includes a full-cycle script (`simulation.py`) that mimics a real customer pattern (submit -> poll -> retrieve).

---

## 🕵️ Task 3: DOM Scraping

**Goal:** Extract specific assets (100+ hidden images vs. 9 visible ones).

*   **Logic:** The script parses the DOM to differentiate between:
    *   **All Images:** Extracted as Base64 strings to `allimages.json`.
    *   **Visible-Only:** Uses computed styles (`display`, `visibility`, `opacity`) and viewport intersection logic to identify what a *human* actually sees, saving to `visible_images_only.json`.

---

## 🏗️ Task 4: System Architecture

**Goal:** Design a scalable scraping infrastructure.

A comprehensive system design is provided in `task4-system-diagram/task4_architecture.md`. It outlines:
*   **Message Queues (RabbitMQ):** For decoupling task submission from execution.
*   **Worker Scaling:** Horizontal scaling strategy for browser nodes.
*   **Monitoring:** ELK Stack & Prometheus integration for health checks.
*   **Database:** Structured storage for results and analytics.

---

## 📦 Universal Setup

Each task folder contains its own `README.md` with specific details, but you can set up the root environment as follows:

```bash
# 1. Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies (Root + Tasks)
pip install -r requirements.txt
pip install -r task1-recaptcha-stealth/requirements.txt
pip install -r task2-api/requirements.txt
pip install -r task3-dom-scraping/requirements.txt

# 3. Install Playwright Browsers
playwright install chromium
```
