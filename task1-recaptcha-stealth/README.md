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
To satisfy the assessment requirement for 250 runs:
```bash
python3 scale_test_context.py --count 250 --headed
```
*Note: This script runs iterations to collect data and verify the 15% @ 0.9 score target.*

---

## 🔍 Diagnostic Tools

If you are getting low scores, use the diagnostic script:
```bash
python3 diagnose.py
```
This script launches the stealth browser and waits for **you** to click the button manually. This eliminates behavior simulation as a variable and tests only the browser fingerprint/reputation.

---

## 🛡️ Stealth Strategy

Our approach uses a multi-layered defense to bypass reCAPTCHA v3 detection:

1. **Binary Evasion**: Instead of using Playwright's bundled Chromium (which is easily flagged), we launch the **system's real Google Chrome** using `subprocess` without the `--enable-automation` flag.
2. **CDP Connection**: We connect Playwright to the running Chrome instance via the Chrome DevTools Protocol (CDP).
3. **Fingerprint Replay**: We inject a real browser fingerprint (User-Agent, WebGL renderer, hardware specs) captured from a real session.
4. **Behavioral Simulation**:
   - `human.py` implements Bezier-curve mouse movements.
   - Randomized scroll patterns and dwell times.
   - Click delays to mimic human reaction time.
5. **Cookie Warm-up**: Visiting `google.com` first ensures the browser has active Google trust signals/cookies.

---

## 📂 Project Structure

- `src/`: Core automation package.
  - `stealth.py`: Chrome launch & fingerprint patching.
  - `human.py`: Mouse/scroll simulation.
  - `interceptor.py`: Network interception for tokens.
  - `extractor.py`: DOM parsing and result extraction.
- `docs/`:
  - `Q1-score-parameters.md`: Explanation of scoring factors (Assessment Q1).
  - `step2-extraction.md`: Technical details on tokens/DOM.
- `record_fingerprint.py`: Utility to capture real browser data.
- `diagnose.py`: Manual testing tool.
- `outputs/`: Where scores, tokens, and fingerprints are stored.

---

## ❓ Q&A and Research

- **Q1 (Score Parameters)**: See [docs/Q1-score-parameters.md](docs/Q1-score-parameters.md)
- **Q2 (reCAPTCHA Research)**: See [docs/Q2-research.md](docs/Q2-research.md) (Answered in the PDF deliverable as per instructions).
