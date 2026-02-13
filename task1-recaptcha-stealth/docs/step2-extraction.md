# Step 2 — reCAPTCHA Extraction Architecture

## Overview

After clicking `<button id="btn">`, the page executes `grecaptcha.execute()`, POSTs the token to the server, and renders the JSON response into `<pre id="out">`.

## DOM Elements Used

| Selector | Type | Data |
|---|---|---|
| `#btn` | `<button>` | Trigger for reCAPTCHA v3 |
| `#out` | `<pre>` | JSON response containing score, success, timestamps |
| POST body | `FormData` | Contains `token` and `action` fields |

## Module Architecture

```
src/
├── main.py          # Orchestrator: navigate → click → wait → extract → save
├── extractor.py     # Parses JSON from #out into structured dict
├── interceptor.py   # Route-based POST interception to capture token
├── __main__.py      # Entry point for python -m src
└── __init__.py      # Package init
```

## Extraction Flow

1. `interceptor.attach()` registers a Playwright route handler on the target URL
2. `main.py` clicks `#btn` to trigger reCAPTCHA
3. The route handler captures the `token` from the outgoing POST `FormData`
4. `main.py` waits for `#out` to contain valid JSON (via `wait_for_function`)
5. `extractor.parse_recaptcha_response()` parses the JSON into a structured dict
6. Results are saved to `outputs/result.json`

## Local Verification

```bash
cd task1-recaptcha-stealth
python -m src
cat outputs/result.json
```

Expected: JSON with `score`, `success`, `token`, and `raw` response fields.
