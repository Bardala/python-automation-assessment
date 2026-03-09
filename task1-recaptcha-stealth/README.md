# Task 1: reCAPTCHA v3 Stealth Automation

This project implements a high-stealth browser automation system designed to achieve human-like reCAPTCHA v3 scores (0.7 - 0.9). It uses a combination of fingerprint recording, real Chrome execution via CDP, and human behavior simulation.

## 📋 Assessment Requirements (Task 1)

As specified in the assessment document:

- **Target URL**: [https://cd.captchaaiplus.com/recaptcha-v3-2.php](https://cd.captchaaiplus.com/recaptcha-v3-2.php)
- **Objective**: Get a good score (0.7 - 0.9) using stealth scripts.
- **Scaled Test**: Automate 250 runs with at least 15% of scores being 0.9.
- **Extraction**: Capture success text and tokens for each run.
- **Connectivity**: Support for IPv4 and IPv6 proxies.
- **Answers**: Explain parameters affecting the score and research reCAPTCHA v3 types.

---

## 🏆 Achievement: 250-Run Scaled Test

**Status: COMPLETED**

- **Success Rate:** >90% of requests achieved a **0.9 Score**.
- **Output File:** `outputs/results_async.json` (contains tokens, scores, and timestamps for all runs).
- **Architecture:** Async/Await with `Playwright` + Custom Stealth.

### ⚠️ Note on Proxy Infrastructure

The solution includes a fully functional **Proxy Rotation System** (see `AsyncScaler` class) capable of handling authenticated proxies and improved stealth via IP rotation.

**Observation:** During testing, the free-tier **Webshare proxies** provided for the assessment were found to be:

1.  **Unreliable:** High latency or complete connection timeouts (verified via `curl` connectivity checks).
2.  **Flagged:** When reachable, they were identified as Data Center IPs, automatically capping reCAPTCHA scores at `0.1` or `0.3` regardless of the stealth implementation.

**Decision:** To demonstrate the _true_ capability of the automation logic, the final scalability benchmarks (250 runs) were executed using a clean residential/local IP. **Result:** The system achieved a **0.9 score** on the vast majority of attempts, meeting the assessment's high-score requirement.

---

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.10+
- Google Chrome installed on your system.
- Ubuntu/Linux environment (tested on Linux).

### 2. Environment Setup

```bash
# Navigate to task directory
cd task1-recaptcha-stealth

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (if not already present)
playwright install chromium
```

---

## 🚀 How to Run

### Step 1: Record your REAL Fingerprint

To achieve a score of 0.9, the script replays a real browser fingerprint.

1. Run the recorder:
   ```bash
   python3 record_fingerprint.py
   ```
2. Open the URL shown (usually `http://localhost:8787`) in your **REAL Google Chrome browser** (not automated).
3. Wait for the page to capture the fingerprint and save it to `outputs/fingerprint.json`.
4. Close the recorder (`Ctrl+C`).

### Step 2: Run a Single Test

Run the main orchestrator to see the stealth automation in action:

```bash
# Standard mode (Headed - opens browser window, score ~0.9)
python3 -m src

# Headless mode (No window - score typically ~0.1)
python3 -m src --headless
```

This will:

- Launch real Chrome via CDP (no automation flags).
- Replay your recorded fingerprint.
- Perform a "cookie warm-up" on Google.com.
- Navigate to the target site.
- Simulate human mouse movements, scrolling, and clicking.
- Intercept the reCAPTCHA token and extract the score.

### Step 3: Run Scaled Testing (250 Runs)

To satisfy the assessment requirement for 250 runs (High Performance Async Mode):

```bash
python3 scale_test_async.py --count 250 --concurrency 5
```

_Note: This script uses an async worker pool to run multiple tests in parallel, drastically reducing runtime while maintaining 0.9 scores._

---

## 🔍 Diagnostic Tools

If you are getting low scores, use the diagnostic script:

```bash
python3 diagnose.py
```

This script launches the stealth browser and waits for **you** to click the button manually. This eliminates behavior simulation as a variable and tests only the browser fingerprint/reputation.

---

## 🛡️ Stealth Strategy

Our approach uses a **defense-in-depth** strategy with 10 distinct anti-detection techniques layered across 4 categories:

| Category               | Techniques                                                                                                       |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Browser Identity**   | Real Chrome via CDP (no automation flags), Fingerprint Replay, playwright-stealth patches, Extended JS injection |
| **Behavioral Mimicry** | Human-like mouse/scroll/click simulation, Google warm-up for trust building                                      |
| **Session Integrity**  | Persistent Chrome profile, Non-invasive token interception                                                       |
| **Infrastructure**     | Proxy support with auth extension, Process lifecycle hygiene                                                     |

> 📖 **Full documentation:** [docs/stealth_strategy.md](docs/stealth_strategy.md) — comprehensive breakdown of every technique with code references, diagrams, and score impact analysis.

---

## 📂 Project Structure

- `config/`: Centralized settings & logging.
- `src/`: Core automation package.
  - `core.py`: **SSOT (Single Source of Truth)** — the canonical `solve_recaptcha()` orchestrator.
  - `stealth.py`: Fingerprint loading, stealth injection & CDP browser launch.
  - `human.py` / `async_human.py`: Human behavior simulation (sync/async).
  - `interceptor.py`: Network interception for token capture.
  - `extractor.py`: DOM parsing and result extraction.
  - `async_manager.py`: Singleton browser lifecycle manager for parallel execution.
  - `async_worker.py`: Async per-iteration test worker.
  - `helpers/`: _(Deprecated — use `src/` root modules instead)_.
- `docs/`:
  - `architecture.md`: Full project architecture with dependency diagrams.
  - `stealth_strategy.md`: Comprehensive stealth techniques documentation.
  - `Q1-score-parameters.md`: Explanation of scoring factors (Assessment Q1).
  - `Q2-research.md`: reCAPTCHA v3 research.
  - `step2-extraction.md`: Technical details on tokens/DOM.
- `record_fingerprint.py`: Utility to capture real browser fingerprint.
- `scale_test_async.py`: **Main Entry Point** for high-performance scaled testing.
- `outputs/`: Where scores, tokens, and fingerprints are stored.

> 📖 **Full architecture:** [docs/architecture.md](docs/architecture.md) — dependency graphs, layered architecture, execution modes, and data flow diagrams.

---

## ❓ Q&A and Research

- **Q1 (Score Parameters)**: See [docs/Q1-score-parameters.md](docs/Q1-score-parameters.md)
- **Q2 (reCAPTCHA Research)**: See [docs/Q2-research.md](docs/Q2-research.md) (Answered in the PDF deliverable as per instructions).
