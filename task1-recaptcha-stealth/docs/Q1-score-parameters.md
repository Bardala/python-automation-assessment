# Task 1 — Q1: How to Improve or Lower the reCAPTCHA v3 Score

## How reCAPTCHA v3 Scoring Works

reCAPTCHA v3 returns a score between **0.0** (bot) and **1.0** (human) based on a risk analysis.
It does **NOT** require any user challenge — it runs silently in the background, analyzing
multiple signals to determine whether the visitor is human or automated.

---

## Parameters That Affect the Score

### 1. Browser Fingerprint (Most Impactful)

| Parameter | Improves Score | Lowers Score |
|---|---|---|
| **`navigator.webdriver`** | `false` (patched via stealth) | `true` (Playwright/Selenium default) |
| **Browser binary** | Real Google Chrome | Headless Chromium / Playwright Chromium |
| **`--enable-automation` flag** | Absent | Present (Playwright injects it by default) |
| **`window.chrome` object** | Present with `runtime`, `app` | Missing or incomplete |
| **`navigator.plugins`** | Realistic plugin list (PDF Viewer, etc.) | Empty array |
| **WebGL renderer** | Real GPU (e.g. `Intel UHD Graphics 630`) | `SwiftShader` or `Mesa OffScreen` |
| **User-Agent string** | Matches real Chrome version | Contains `HeadlessChrome` or outdated version |
| **`navigator.platform`** | Consistent with UA (e.g. `Linux x86_64`) | Mismatched or generic value |
| **Canvas fingerprint** | Unique, consistent across visits | Randomized or missing |

**Key Insight**: Playwright's bundled Chromium is fundamentally different from real Chrome.
reCAPTCHA can detect this through binary-level fingerprinting even with JS patches applied.
Using `channel='chrome'` or launching real Chrome via subprocess is essential.

### 2. User Behavior Signals

| Parameter | Improves Score | Lowers Score |
|---|---|---|
| **Mouse movements** | Natural, randomized paths with varying speed | No mouse events at all |
| **Scrolling** | Organic scroll patterns (variable speed, up/down) | No scroll events |
| **Click patterns** | Hover → pause → click (human-like timing) | Instant programmatic `.click()` |
| **Time on page** | 3-10 seconds of interaction before action | Instant action (< 1 second) |
| **Keyboard events** | Present (typing, tab) | Absent |
| **Touch events** | Consistent with device type | Mismatch (touch on desktop) |

### 3. Network & Environment

| Parameter | Improves Score | Lowers Score |
|---|---|---|
| **IP reputation** | Residential IP, clean history | Data center IP, VPN, known proxy |
| **Google cookies** | Present (`NID`, `1P_JAR`, `CONSENT`) | Missing (fresh profile) |
| **Request frequency** | Normal human pace | Rapid sequential requests |
| **Timezone / Locale** | Consistent with IP geolocation | Mismatch (e.g. US timezone with EU IP) |
| **TLS fingerprint** | Matches real Chrome `JA3` hash | Non-browser or outdated TLS config |

### 4. Page Context

| Parameter | Improves Score | Lowers Score |
|---|---|---|
| **Referrer** | Natural navigation flow | Direct access with no referrer |
| **Previous page visits** | Visit google.com first (cookie warm-up) | Jump directly to target |
| **Session duration** | Multiple page interactions over time | Single-page single-action sessions |
| **reCAPTCHA script load** | Loaded normally, not blocked | Blocked or modified by extensions |

---

## How We Improved the Score: 0.1 → 0.9

### What Failed (Score: 0.1)
1. Using Playwright's built-in Chromium → binary detected as automation tool
2. `--disable-blink-features=AutomationControlled` flag → Chrome shows warning banner AND breaks `grecaptcha.execute`
3. `playwright-stealth` patches alone → insufficient against binary fingerprinting
4. Persistent context with fresh cookies → no Google trust signals

### What Worked (Score: 0.9)
1. **Fingerprint Recording**: Captured real browser fingerprint from user's actual Chrome session
   - User-Agent: `Chrome/144.0.0.0` (real version)
   - WebGL: `ANGLE (Intel, Mesa Intel(R) UHD Graphics 630)` (real GPU)
   - Platform, vendor, hardware concurrency, device memory — all from real browser
2. **Real Chrome via CDP**: Launched system Chrome via `subprocess` (no `--enable-automation`), connected Playwright via `connect_over_cdp`
3. **Stealth Patches**: Applied via `playwright-stealth` to patch remaining signals (`navigator.webdriver`, plugins, etc.)
4. **Human Behavior Simulation**: Mouse movements, scrolling, hover-before-click, page dwell time
5. **Cookie Warm-Up**: Visited `google.com` first to establish Google cookie trust

---

## Summary

The single most important factor for reCAPTCHA v3 scoring is the **browser binary fingerprint**.
No amount of JavaScript patching can overcome detection of Playwright's bundled Chromium.
Using real Chrome with a recorded fingerprint and clean launch (no automation flags) is the
foundation. Behavior simulation and cookie warm-up further improve the score.
