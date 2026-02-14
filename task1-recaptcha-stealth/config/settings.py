"""Global Project Configuration."""

import os

# --- Path Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
PROFILE_DIR = os.path.join(PROJECT_ROOT, ".chrome_profile")
FINGERPRINT_PATH = os.path.join(OUTPUT_DIR, "fingerprint.json")

# --- reCAPTCHA Constants ---
TARGET_URL = "https://cd.captchaaiplus.com/recaptcha-v3-2.php"
GOOGLE_URL = "https://www.google.com"

# --- Chrome Configuration ---
DEFAULT_DEBUG_PORT = 9222
CONCURRENCY_LIMIT = 5  # Max parallel browser contexts

# --- Timeout Settings (ms) ---
NAV_TIMEOUT = 60000        # Page load timeout
WARMUP_TIMEOUT = 60000     # Google warm-up timeout
EXTRACTION_TIMEOUT = 20000 # Wait for results JSON

# --- Stealth Config ---
USER_AGENT_FALLBACK = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# --- Ensure Directories Exist ---
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)
