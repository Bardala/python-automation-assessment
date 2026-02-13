"""Extracts reCAPTCHA score, success status, and metadata from the #out JSON response."""

import json


def parse_recaptcha_response(raw_json: str) -> dict:
    """Parse the JSON string rendered in the #out element.

    Args:
        raw_json: Raw JSON text from the <pre id="out"> element.

    Returns:
        Dict with extracted fields: score, success, action, challenge_ts, hostname.
    """
    data = json.loads(raw_json)
    google = data.get("google_response", {})

    return {
        "score": google.get("score"),
        "success": google.get("success"),
        "action": google.get("action"),
        "challenge_ts": google.get("challenge_ts"),
        "hostname": google.get("hostname"),
        "pass": data.get("pass"),
        "raw": data,
    }
