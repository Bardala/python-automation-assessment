# 🛡️ Stealth Strategy — Implemented Techniques

> A deep dive into every anti-detection technique implemented in `task1-recaptcha-stealth`,
> explaining **what** each technique does, **why** it matters for reCAPTCHA v3 scoring,
> and **where** it is implemented in the codebase.

---

## Table of Contents

1. [Threat Model: What reCAPTCHA v3 Detects](#1-threat-model-what-recaptcha-v3-detects)
2. [Strategy Overview](#2-strategy-overview)
3. [Technique 1: Real Chrome via CDP (No Automation Flags)](#3-technique-1-real-chrome-via-cdp-no-automation-flags)
4. [Technique 2: Real Browser Fingerprint Replay](#4-technique-2-real-browser-fingerprint-replay)
5. [Technique 3: playwright-stealth Patches](#5-technique-3-playwright-stealth-patches)
6. [Technique 4: Extended Fingerprint Injection (JavaScript)](#6-technique-4-extended-fingerprint-injection-javascript)
7. [Technique 5: Human Behavior Simulation](#7-technique-5-human-behavior-simulation)
8. [Technique 6: Google Warm-Up (Trust Signal Building)](#8-technique-6-google-warm-up-trust-signal-building)
9. [Technique 7: Persistent Chrome Profile](#9-technique-7-persistent-chrome-profile)
10. [Technique 8: Token Interception via Route Handling](#10-technique-8-token-interception-via-route-handling)
11. [Technique 9: Proxy Support with Auth Extension](#11-technique-9-proxy-support-with-auth-extension)
12. [Technique 10: Process Lifecycle Hygiene](#12-technique-10-process-lifecycle-hygiene)
13. [Technique Stack Diagram](#13-technique-stack-diagram)
14. [Score Impact Analysis](#14-score-impact-analysis)

---

## 1. Threat Model: What reCAPTCHA v3 Detects

reCAPTCHA v3 is a **behavioral scoring engine** — it does not present challenges. Instead, it silently monitors the user's session and assigns a score from `0.0` (bot) to `1.0` (human) based on multiple signals:

```mermaid
mindmap
  root((reCAPTCHA v3<br/>Detection))
    Browser Fingerprint
      navigator.webdriver === true
      Missing chrome.runtime
      Inconsistent User-Agent
      WebGL renderer mismatch
      Headless-mode indicators
    Behavioral Analysis
      Mouse movement patterns
      Scroll behavior
      Click precision and timing
      Dwell time on page
      Keyboard input patterns
    Session Context
      Referrer chain
      Cookie history
      IP reputation
      Previous Google interactions
    JavaScript Environment
      Automation framework traces
      Modified prototype chains
      Missing browser APIs
      Plugin/extension anomalies
```

Our stealth strategy addresses **every category** in this threat model.

---

## 2. Strategy Overview

The system implements a **defense-in-depth** approach with 10 distinct techniques layered across 4 categories:

```mermaid
graph TB
    subgraph "Category 1: Browser Identity"
        T1["🔧 Real Chrome via CDP"]
        T2["🎭 Fingerprint Replay"]
        T3["🩹 playwright-stealth Patches"]
        T4["💉 Extended JS Injection"]
    end

    subgraph "Category 2: Behavioral Mimicry"
        T5["🖱️ Human Behavior Sim"]
        T6["🌐 Google Warm-Up"]
    end

    subgraph "Category 3: Session Integrity"
        T7["💾 Persistent Profile"]
        T8["📡 Token Interception"]
    end

    subgraph "Category 4: Infrastructure"
        T9["🔒 Proxy + Auth Extension"]
        T10["🧹 Process Hygiene"]
    end

    T1 --> Result["🎯 Score: 0.7 — 0.9"]
    T2 --> Result
    T3 --> Result
    T4 --> Result
    T5 --> Result
    T6 --> Result
    T7 --> Result
    T8 --> Result
    T9 --> Result
    T10 --> Result

    style Result fill:#4CAF50,color:#fff,stroke-width:3px
```

---

## 3. Technique 1: Real Chrome via CDP (No Automation Flags)

### What It Does

Instead of using Playwright's built-in browser launch (which adds `--enable-automation` and other flags), the system launches a **real system-installed Chrome binary** via `subprocess.Popen`, then connects to it using the **Chrome DevTools Protocol (CDP)**.

### Why It Matters

When Playwright launches Chrome normally, it adds several automation flags:

- `--enable-automation` — Tells websites the browser is automated
- `--disable-background-networking` — Breaks normal browser behavior
- `--enable-blink-features=IdleDetection` — Automation-specific feature

These flags are trivially detectable by reCAPTCHA.

### How It's Implemented

**File:** `src/stealth.py` → `create_stealth_persistent()` (lines 182–265)  
**File:** `src/helpers/stealth.py` → `create_stealth_persistent()` (lines 180–265)

```python
# 1. Launch real Chrome — NO automation flags
chrome_args = [
    chrome_binary,
    f"--remote-debugging-port={debug_port}",
    f"--user-data-dir={PROFILE_DIR}",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-infobars",
    "--disable-dev-shm-usage",
    "about:blank",
]

chrome_process = subprocess.Popen(
    chrome_args,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# 2. Connect Playwright to the ALREADY RUNNING Chrome via CDP
pw = sync_playwright().start()
browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
```

### Key Design Decisions

| Decision                                             | Rationale                                                      |
| ---------------------------------------------------- | -------------------------------------------------------------- |
| `subprocess.Popen` instead of `pw.chromium.launch()` | Avoids Playwright injecting automation flags                   |
| `stdout=DEVNULL, stderr=DEVNULL`                     | Prevents pipe buffer blocking on long runs                     |
| `--no-first-run`                                     | Suppresses "Welcome to Chrome" dialogs                         |
| `--disable-infobars`                                 | Removes "Chrome is being controlled by automated software" bar |
| `about:blank` as initial URL                         | Fast startup, no network requests before stealth is applied    |

### Detection It Bypasses

```mermaid
flowchart LR
    A["reCAPTCHA checks:<br/>window.chrome.runtime"] -->|"Normal Playwright"| B["❌ undefined<br/>(detected as bot)"]
    A -->|"Our CDP approach"| C["✅ Present<br/>(looks like real Chrome)"]

    D["reCAPTCHA checks:<br/>navigator.webdriver"] -->|"Normal Playwright"| E["❌ true<br/>(automation flag set)"]
    D -->|"Our CDP approach"| F["✅ false<br/>(patched via stealth)"]
```

---

## 4. Technique 2: Real Browser Fingerprint Replay

### What It Does

Captures the **exact fingerprint** of a real user's browser session (User-Agent, screen resolution, WebGL renderer, hardware specs, timezone, etc.) and replays it during automated sessions, creating an internally consistent browser identity.

### Why It Matters

reCAPTCHA checks for **fingerprint consistency**. If the User-Agent says "Chrome 144 on Linux" but the WebGL renderer reports a Windows GPU, or `hardwareConcurrency` doesn't match the claimed platform, the session is flagged as suspicious.

### How It's Implemented

#### Phase 1: Recording (One-Time Setup)

**File:** `record_fingerprint.py`

A local HTTP server (port 8787) serves a page that collects the user's real fingerprint via JavaScript APIs:

```javascript
// Collected properties (excerpt from record_fingerprint.py)
fp.userAgent = navigator.userAgent;
fp.platform = navigator.platform;
fp.hardwareConcurrency = navigator.hardwareConcurrency;
fp.deviceMemory = navigator.deviceMemory;
fp.maxTouchPoints = navigator.maxTouchPoints;
fp.screen = { width, height, colorDepth, pixelDepth, ... };
fp.webgl = { vendor, renderer, version, ... };  // GPU fingerprint
fp.languages = Array.from(navigator.languages);
fp.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
fp.plugins = [...];  // PDF viewers, etc.
fp.connection = { effectiveType, downlink, rtt };
fp.permissions = { geolocation, notifications, camera, microphone };
```

The fingerprint is saved to `outputs/fingerprint.json`.

#### Phase 2: Replay (Every Run)

**File:** `src/stealth.py` → `_load_fingerprint()`, `_build_stealth()`, `_build_context_options()`, `_extra_fingerprint_script()`  
**File:** `src/helpers/stealth.py` → same functions

The fingerprint is loaded (cached via `@lru_cache`) and applied at multiple levels:

```mermaid
flowchart TD
    A["outputs/fingerprint.json"] -->|"_load_fingerprint()"| B["In-Memory Fingerprint Dict"]

    B --> C["_build_stealth(fp)"]
    C -->|"Configures"| C1["User-Agent override"]
    C -->|"Configures"| C2["Platform override"]
    C -->|"Configures"| C3["Vendor override"]
    C -->|"Configures"| C4["WebGL vendor/renderer override"]
    C -->|"Configures"| C5["navigator.webdriver = false"]
    C -->|"Configures"| C6["chrome.runtime injection"]

    B --> D["_build_context_options(fp)"]
    D -->|"Sets"| D1["viewport (matching screen)"]
    D -->|"Sets"| D2["locale (matching language)"]
    D -->|"Sets"| D3["timezone_id"]
    D -->|"Sets"| D4["device_scale_factor"]

    B --> E["_extra_fingerprint_script(fp)"]
    E -->|"Injects JS for"| E1["navigator.hardwareConcurrency"]
    E -->|"Injects JS for"| E2["navigator.deviceMemory"]
    E -->|"Injects JS for"| E3["navigator.maxTouchPoints"]
    E -->|"Injects JS for"| E4["navigator.languages"]

    style A fill:#FF9800,color:#fff
    style B fill:#9C27B0,color:#fff
```

### Properties Replayed

| Property                         | Source in fingerprint.json     | Applied Via                            |
| -------------------------------- | ------------------------------ | -------------------------------------- |
| `navigator.userAgent`            | `userAgent`                    | `playwright-stealth` + context options |
| `navigator.platform`             | `platform`                     | `playwright-stealth`                   |
| `navigator.vendor`               | `vendor`                       | `playwright-stealth`                   |
| `navigator.hardwareConcurrency`  | `hardwareConcurrency`          | JS `Object.defineProperty()` injection |
| `navigator.deviceMemory`         | `deviceMemory`                 | JS `Object.defineProperty()` injection |
| `navigator.maxTouchPoints`       | `maxTouchPoints`               | JS `Object.defineProperty()` injection |
| `navigator.languages`            | `languages`                    | JS `Object.defineProperty()` injection |
| `screen.width / height`          | `screen.width, screen.height`  | Playwright context viewport/screen     |
| `window.devicePixelRatio`        | `devicePixelRatio`             | Playwright `device_scale_factor`       |
| `Intl.DateTimeFormat().timeZone` | `timezone`                     | Playwright `timezone_id`               |
| WebGL vendor/renderer            | `webgl.vendor, webgl.renderer` | `playwright-stealth` WebGL override    |

---

## 5. Technique 3: playwright-stealth Patches

### What It Does

The `playwright-stealth` library applies a set of known patches to make Playwright-controlled browsers undetectable by common bot detection scripts.

### Why It Matters

Even with CDP connection (Technique 1), there are still JavaScript-level artifacts that reveal automation. `playwright-stealth` patches these across the entire browsing context.

### How It's Implemented

**File:** `src/stealth.py` → `_build_stealth()` (lines 33–49)

```python
def _build_stealth(fp: dict | None) -> Stealth:
    kwargs = {
        "chrome_runtime": True,           # Inject window.chrome.runtime
        "navigator_webdriver": True,       # Patch navigator.webdriver → false
    }

    if fp:
        kwargs["navigator_user_agent_override"] = fp.get("userAgent")
        kwargs["navigator_platform_override"] = fp.get("platform")
        kwargs["navigator_vendor_override"] = fp.get("vendor")

        if fp.get("webgl"):
            kwargs["webgl_vendor_override"] = fp["webgl"].get("vendor")
            kwargs["webgl_renderer_override"] = fp["webgl"].get("renderer")

    return Stealth(**kwargs)
```

### Patches Applied

```mermaid
graph LR
    subgraph "playwright-stealth Patches"
        A["chrome_runtime = True"]
        B["navigator_webdriver = True"]
        C["navigator_user_agent_override"]
        D["navigator_platform_override"]
        E["navigator_vendor_override"]
        F["webgl_vendor_override"]
        G["webgl_renderer_override"]
    end

    A -->|"Injects"| A1["window.chrome = {<br/>  runtime: {<br/>    connect: fn,<br/>    sendMessage: fn<br/>  }<br/>}"]

    B -->|"Patches"| B1["Object.defineProperty(<br/>  navigator, 'webdriver',<br/>  {get: () => false}<br/>)"]

    C -->|"Overrides"| C1["navigator.userAgent<br/>matches real browser"]

    F -->|"Overrides"| F1["WebGLRenderingContext<br/>.getParameter()<br/>matches real GPU"]

    style A fill:#E91E63,color:#fff
    style B fill:#E91E63,color:#fff
```

### Detection Tests Bypassed

| Test                              | Without Stealth |      With Stealth       |
| --------------------------------- | :-------------: | :---------------------: |
| `navigator.webdriver`             |    `true` ❌    |       `false` ✅        |
| `window.chrome`                   | `undefined` ❌  |  `{runtime: {...}}` ✅  |
| `window.chrome.runtime`           | `undefined` ❌  | `{connect: fn, ...}` ✅ |
| WebGL renderer fingerprint        |  Mismatched ❌  |   Matches real GPU ✅   |
| `navigator.userAgent` consistency |   Generic ❌    |    Real Chrome UA ✅    |

---

## 6. Technique 4: Extended Fingerprint Injection (JavaScript)

### What It Does

Injects custom JavaScript via `context.add_init_script()` to override navigator properties that `playwright-stealth` does not cover.

### Why It Matters

`playwright-stealth` covers the most common detection vectors, but reCAPTCHA also checks less common properties like `hardwareConcurrency`, `deviceMemory`, and `maxTouchPoints`. Inconsistencies in these values can reduce the score.

### How It's Implemented

**File:** `src/stealth.py` → `_extra_fingerprint_script()` (lines 88–123)  
**File:** `src/helpers/stealth.py` → `_extra_fingerprint_script()` (lines 84–119)

```python
def _extra_fingerprint_script(fp: dict | None) -> str:
    overrides = []

    # Hardware concurrency (CPU cores)
    hc = fp.get("hardwareConcurrency")
    if hc:
        overrides.append(
            f"Object.defineProperty(navigator, 'hardwareConcurrency', "
            f"{{get: () => {hc}}});"
        )

    # Device memory (RAM in GB)
    dm = fp.get("deviceMemory")
    if dm:
        overrides.append(
            f"Object.defineProperty(navigator, 'deviceMemory', "
            f"{{get: () => {dm}}});"
        )

    # Max touch points (0 for desktop, >0 for mobile)
    mtp = fp.get("maxTouchPoints", 0)
    overrides.append(
        f"Object.defineProperty(navigator, 'maxTouchPoints', "
        f"{{get: () => {mtp}}});"
    )

    # Languages array
    langs = fp.get("languages")
    if langs:
        overrides.append(
            f"Object.defineProperty(navigator, 'languages', "
            f"{{get: () => {json.dumps(langs)}}});"
        )

    return "\n".join(overrides)
```

This script runs **before any page JavaScript** via `context.add_init_script()`, ensuring reCAPTCHA's detection scripts see consistent values from the first moment.

### Example Generated Script

For the recorded fingerprint in `outputs/fingerprint.json`:

```javascript
Object.defineProperty(navigator, "hardwareConcurrency", { get: () => 8 });
Object.defineProperty(navigator, "deviceMemory", { get: () => 8 });
Object.defineProperty(navigator, "maxTouchPoints", { get: () => 0 });
Object.defineProperty(navigator, "languages", { get: () => ["en-US", "en"] });
```

---

## 7. Technique 5: Human Behavior Simulation

### What It Does

Simulates realistic mouse movements, scrolling, clicking, and dwell time to produce behavioral signals that match human interaction patterns.

### Why It Matters

reCAPTCHA v3 heavily weights **behavioral analysis**. A bot that navigates directly to a button and clicks it in 100ms will score `0.1`. A session with natural mouse movement, scroll exploration, and appropriate dwell time scores `0.7–0.9`.

### How It's Implemented

**Sync path:** `src/human.py` (75 lines)  
**Async path:** `src/helpers/async_human.py` (44 lines)  
**Orchestrator:** `src/core.py` → `_simulate_human_behavior()` (lines 91–96)

#### Mouse Movements

```python
def random_mouse_movements(page: Page, count: int = 5) -> None:
    viewport = page.viewport_size
    for _ in range(count):
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        # Multiple steps create a curved path, not a teleport
        page.mouse.move(x, y, steps=random.randint(3, 8))
        time.sleep(random.uniform(0.05, 0.2))
```

```mermaid
graph LR
    subgraph "Bot Click Pattern ❌"
        B1["(0,0)"] -->|"instant teleport"| B2["(btn_x, btn_y)"]
        B2 -->|"instant"| B3["click()"]
    end

    subgraph "Human Click Pattern ✅"
        H1["(random_x, random_y)"] -->|"3-8 steps,<br/>50-200ms pause"| H2["(random_x2, random_y2)"]
        H2 -->|"3-8 steps"| H3["(random_x3, random_y3)"]
        H3 -->|"5-12 steps"| H4["(btn_area, ±30-70%)"]
        H4 -->|"100-300ms hover"| H5["click()"]
    end
```

#### Scroll Simulation

```python
def random_scroll(page: Page) -> None:
    # Scroll DOWN in small increments (2-4 times)
    for _ in range(random.randint(2, 4)):
        scroll_amount = random.randint(80, 200)
        page.mouse.wheel(0, scroll_amount)
        time.sleep(random.uniform(0.2, 0.5))

    time.sleep(random.uniform(0.3, 0.8))  # Pause at bottom

    # Scroll BACK UP (1-3 times)
    for _ in range(random.randint(1, 3)):
        scroll_amount = random.randint(80, 200)
        page.mouse.wheel(0, -scroll_amount)
        time.sleep(random.uniform(0.2, 0.5))
```

#### Human-Like Click (`human_click`)

```python
def human_click(page: Page, selector: str) -> None:
    element = page.locator(selector)
    box = element.bounding_box()

    if box:
        # Click at a RANDOM point within the element (not dead center)
        target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
        target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)

        # Multi-step approach movement
        page.mouse.move(target_x, target_y, steps=random.randint(5, 12))

        # Hover pause before clicking (humans don't click instantly)
        time.sleep(random.uniform(0.1, 0.3))

        page.mouse.click(target_x, target_y)
```

### Behavioral Signal Timeline

```mermaid
gantt
    title Human Behavior Simulation Timeline
    dateFormat X
    axisFormat %Ls

    section Warm-Up Phase
    Google visit                    :a1, 0, 1500
    Mouse movements (2x)           :a2, 1500, 1900

    section Target Page
    Navigate to target              :b1, 1900, 3900
    Mouse movements (3x)           :b2, 3900, 4800
    Random scroll (down + up)      :b3, 4800, 6200
    Dwell time (2.0-3.5s)          :b4, 6200, 9200

    section Interaction
    Approach #btn (5-12 steps)     :c1, 9200, 9600
    Hover pause                    :c2, 9600, 9900
    Click                          :c3, 9900, 10000
    Wait for result                :c4, 10000, 12000
```

### Randomization Ranges

| Action           |  Min |  Max | Unit  |
| ---------------- | ---: | ---: | ----- |
| Mouse move steps |    3 |   12 | steps |
| Inter-move pause |   50 |  200 | ms    |
| Scroll amount    |   80 |  200 | px    |
| Scroll pause     |  200 |  500 | ms    |
| Bottom pause     |  300 |  800 | ms    |
| Pre-click hover  |  100 |  300 | ms    |
| Dwell time       | 2000 | 3500 | ms    |
| Warm-up dwell    |  800 | 1500 | ms    |

---

## 8. Technique 6: Google Warm-Up (Trust Signal Building)

### What It Does

Before navigating to the reCAPTCHA-protected target page, the system first visits `google.com`, performs mouse movements, and dwells briefly. This establishes a trusted session context.

### Why It Matters

reCAPTCHA v3 is **Google's product**. It has deep integration with Google's cookie/session infrastructure. A browser session that has recently interacted with Google's domain is inherently more trusted. Sessions that arrive "cold" to a reCAPTCHA-protected page with no prior Google interaction are suspicious.

### How It's Implemented

**File:** `src/core.py` → `_perform_warmup()` (lines 79–88)

```python
def _perform_warmup(page: Page):
    """Visit Google to establish a trusted session context."""
    try:
        page.goto(GOOGLE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(random.randint(800, 1500))
        random_mouse_movements(page, count=2)
    except Exception as e:
        print(f"  ⚠️  Warm-up failed (non-critical): {e}")
```

### Trust Building Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Google as google.com
    participant Target as Target Page
    participant reCAPTCHA as reCAPTCHA v3

    Browser->>Google: GET google.com
    Google-->>Browser: Set Google cookies<br/>(NID, 1P_JAR, etc.)
    Note over Browser: Mouse movements (2x)
    Note over Browser: Dwell: 800-1500ms

    Browser->>Target: GET target page
    Note over Browser: reCAPTCHA loads,<br/>checks Google cookies
    reCAPTCHA-->>reCAPTCHA: "This session has<br/>trusted Google cookies"
    Note over reCAPTCHA: +0.1 to +0.3 score boost
```

### Error Handling

The warm-up is wrapped in a `try/except` with suppressed errors because:

- Warm-up failure should **not** abort the test
- Network issues (DNS, timeout) are common but non-critical
- The test can still succeed with a slightly lower score without warm-up

---

## 9. Technique 7: Persistent Chrome Profile

### What It Does

Chrome is launched with a `--user-data-dir` pointing to `.chrome_profile/`, which persists cookies, local storage, IndexedDB, and Chrome's internal state across runs.

### Why It Matters

reCAPTCHA tracks session history. A browser with existing Google cookies, cached data, and a normal browsing history looks far more legitimate than a fresh, empty profile.

### How It's Implemented

**File:** `config/settings.py` (line 8)

```python
PROFILE_DIR = os.path.join(PROJECT_ROOT, ".chrome_profile")
```

**File:** `src/stealth.py` (line 209)

```python
chrome_args = [
    chrome_binary,
    f"--user-data-dir={PROFILE_DIR}",   # ← Persistent profile
    ...
]
```

### What Gets Persisted

```mermaid
graph TD
    subgraph ".chrome_profile/"
        A["Cookies<br/><i>Google NID, 1P_JAR, etc.</i>"]
        B["Local Storage<br/><i>Site preferences</i>"]
        C["IndexedDB<br/><i>Application data</i>"]
        D["Cache<br/><i>Faster page loads</i>"]
        E["Chrome Preferences<br/><i>Browser settings</i>"]
        F["Login Data<br/><i>(encrypted)</i>"]
    end

    G["First Run"] -->|"Creates"| A
    G -->|"Creates"| E
    H["Subsequent Runs"] -->|"Reuses all"| A
    H -->|"Reuses all"| B
    H -->|"Reuses all"| C
    H -->|"Reuses all"| D
    H -->|"Reuses all"| E

    Note["🔑 Key Benefit:<br/>Google cookies from warm-up<br/>persist across runs,<br/>building trust over time"]

    style Note fill:#4CAF50,color:#fff
```

---

## 10. Technique 8: Token Interception via Route Handling

### What It Does

Intercepts the outgoing POST request that contains the reCAPTCHA token **before** it reaches the server, allowing the system to capture the token for analysis without modifying the page's JavaScript.

### Why It Matters

The reCAPTCHA token is generated client-side by `grecaptcha.execute()` and sent via `fetch()` as `multipart/form-data`. Intercepting it at the network layer (via Playwright's route API) is non-invasive — it doesn't inject any JavaScript that could be detected.

### How It's Implemented

**File:** `src/interceptor.py` → `TokenInterceptor` class (46 lines)

```python
class TokenInterceptor:
    def __init__(self):
        self.token: str | None = None

    def attach(self, page: Page, target_url: str) -> None:
        page.route(target_url, self._handle_route)

    def _handle_route(self, route: Route) -> None:
        request = route.request
        if request.method == "POST" and request.post_data:
            body = request.post_data
            # Parse multipart/form-data to extract token
            match = re.search(
                r'name="token"\r?\n\r?\n(.+?)(?:\r?\n--)', body, re.DOTALL
            )
            if match:
                self.token = match.group(1).strip()
            else:
                # Fallback: URL-encoded form
                for part in body.split("&"):
                    if part.startswith("token="):
                        self.token = part[len("token="):]
        route.continue_()  # ← Always continues the request
```

### Interception Flow

```mermaid
sequenceDiagram
    participant Page as Browser Page
    participant Route as Playwright Route Handler
    participant Server as Target Server

    Note over Page: grecaptcha.execute() runs
    Page->>Page: Gets token from Google

    Page->>Route: fetch(TARGET_URL, {body: FormData{token}})
    Note over Route: _handle_route() fires
    Route->>Route: Extract token via regex
    Route->>Route: Store in self.token

    Route->>Server: route.continue_() → forward original request
    Server-->>Page: JSON response {google_response: {score: ...}}
    Note over Page: Response rendered in #out
```

### Why Not Inject JavaScript?

| Approach                              | Pros                                                        | Cons                                      |
| ------------------------------------- | ----------------------------------------------------------- | ----------------------------------------- |
| **Route interception** (our approach) | Non-invasive, no JS footprint, handles all encoding formats | Requires regex parsing of multipart data  |
| **JS injection** (`page.evaluate`)    | Simpler parsing                                             | Modifies JS context, possibly detected    |
| **Response interception**             | Can modify response                                         | Changes server behavior, breaks integrity |

---

## 11. Technique 9: Proxy Support with Auth Extension

### What It Does

Supports HTTP proxy servers with authentication by dynamically creating a Chrome extension that handles the `407 Proxy Authentication Required` challenge. This avoids the authentication popup that Chrome shows for proxies with credentials.

### Why It Matters

Using multiple proxies allows:

- **IP rotation** to avoid rate limiting
- **Geographical diversity** for more realistic traffic patterns
- Testing from different network conditions

Chrome's built-in `--proxy-server` flag does not support `username:password` authentication, so maintaining a seamless proxy auth requires this extension approach.

### How It's Implemented

**File:** `src/async_manager.py` → `AsyncBrowserManager._create_proxy_auth_extension()` (lines 35–116)

```python
def _create_proxy_auth_extension(self, proxy_url: str) -> str:
    # Parse proxy URL for credentials
    parsed = urlparse(proxy_url)
    username = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port

    # Create a temporary Chrome extension directory
    ext_dir = os.path.join(PROFILE_DIR, "proxy_auth_ext")

    # manifest.json — declares permissions for proxy + webRequest
    # background.js — intercepts auth challenges and responds automatically
```

The extension uses Chrome's `webRequest.onAuthRequired` API to automatically supply credentials when the proxy challenges the connection.

### Proxy Validation

Before using a proxy for a batch of runs, it's validated using `curl`:

```python
async def _validate_proxy(self, proxy):
    proc = await asyncio.create_subprocess_exec(
        "curl", "--max-time", "5", "-I", "-x", proxy,
        "https://www.google.com",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()
    return proc.returncode == 0
```

---

## 12. Technique 10: Process Lifecycle Hygiene

### What It Does

Ensures clean Chrome process management across runs by killing stale processes, removing lock files, and waiting for port availability before connecting.

### Why It Matters

Leftover Chrome processes from crashed or interrupted runs can:

- Block the debugging port
- Corrupt the Chrome profile (lock files)
- Cause "Target page, context or browser has been closed" errors
- Lead to resource exhaustion over many iterations

### How It's Implemented

**File:** `src/stealth.py` → `_kill_existing_chrome()` (lines 138–166)  
**File:** `src/stealth.py` → `_wait_for_port()` (lines 169–179)

```python
def _kill_existing_chrome(debug_port: int) -> None:
    # 1. Kill by port (lsof + kill -9)
    result = subprocess.run(
        ["lsof", "-ti", f":{debug_port}"],
        capture_output=True, text=True,
    )
    if result.stdout.strip():
        for pid in result.stdout.strip().split("\n"):
            subprocess.run(["kill", "-9", pid], capture_output=True)

    # 2. Kill by process name pattern
    subprocess.run(
        ["pkill", "-f", f"remote-debugging-port={debug_port}"],
        capture_output=True,
    )
    time.sleep(1)

    # 3. Remove stale Chrome lock files
    for lock_file in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        lock_path = os.path.join(PROFILE_DIR, lock_file)
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass
```

### Cleanup Sequence

```mermaid
flowchart TD
    A["Start: _kill_existing_chrome()"] --> B["lsof -ti :9222"]
    B -->|"PIDs found"| C["kill -9 each PID"]
    B -->|"No PIDs"| D["Continue"]
    C --> D

    D --> E["pkill -f remote-debugging-port=9222"]
    E --> F["sleep(1)"]
    F --> G["Remove SingletonLock"]
    G --> H["Remove SingletonSocket"]
    H --> I["Remove SingletonCookie"]
    I --> J["Port is now clear ✅"]

    J --> K["Launch new Chrome"]
    K --> L["_wait_for_port(9222, timeout=10)"]
    L -->|"Port open"| M["Connect via CDP ✅"]
    L -->|"Timeout"| N["RuntimeError ❌"]

    style J fill:#4CAF50,color:#fff
    style N fill:#F44336,color:#fff
```

---

## 13. Technique Stack Diagram

This shows how all 10 techniques work together in a single execution:

```mermaid
graph TB
    subgraph "Infrastructure Layer"
        T10["🧹 Process Hygiene<br/><i>Kill stale Chrome,<br/>remove locks</i>"]
        T9["🔒 Proxy + Auth Extension<br/><i>IP rotation,<br/>transparent auth</i>"]
    end

    subgraph "Browser Identity Layer"
        T1["🔧 Real Chrome via CDP<br/><i>No automation flags</i>"]
        T7["💾 Persistent Profile<br/><i>Cookies, cache,<br/>browsing history</i>"]
        T2["🎭 Fingerprint Replay<br/><i>UA, screen, GPU,<br/>timezone match real browser</i>"]
        T3["🩹 playwright-stealth<br/><i>webdriver=false,<br/>chrome.runtime present</i>"]
        T4["💉 Extended JS Injection<br/><i>hardwareConcurrency,<br/>deviceMemory, languages</i>"]
    end

    subgraph "Behavioral Layer"
        T6["🌐 Google Warm-Up<br/><i>Trusted cookies,<br/>session context</i>"]
        T5["🖱️ Human Simulation<br/><i>Mouse, scroll, click,<br/>dwell time</i>"]
    end

    subgraph "Data Layer"
        T8["📡 Token Interception<br/><i>Non-invasive capture<br/>via route handler</i>"]
    end

    T10 --> T1
    T9 --> T1
    T1 --> T7
    T7 --> T2
    T2 --> T3
    T3 --> T4
    T4 --> T6
    T6 --> T5
    T5 --> T8
    T8 --> Result["🎯 Score: 0.7 — 0.9"]

    style Result fill:#4CAF50,color:#fff,stroke-width:3px
    style T1 fill:#9C27B0,color:#fff
    style T5 fill:#2196F3,color:#fff
    style T2 fill:#FF9800,color:#fff
```

---

## 14. Score Impact Analysis

Each technique contributes to the final reCAPTCHA v3 score. While Google does not publish the exact weights, empirical testing shows the following approximate impact:

```mermaid
graph LR
    subgraph "Without Stealth"
        A["Raw Playwright<br/>Score: 0.1"]
    end

    subgraph "Cumulative Impact"
        B["+CDP Launch<br/>Score: ~0.3"]
        C["+Fingerprint Replay<br/>Score: ~0.4"]
        D["+Stealth Patches<br/>Score: ~0.5"]
        E["+Human Simulation<br/>Score: ~0.6"]
        F["+Google Warm-Up<br/>Score: ~0.7"]
        G["+Persistent Profile<br/>Score: 0.7-0.9"]
    end

    A --> B --> C --> D --> E --> F --> G

    style A fill:#F44336,color:#fff
    style B fill:#FF5722,color:#fff
    style C fill:#FF9800,color:#fff
    style D fill:#FFC107,color:#000
    style E fill:#CDDC39,color:#000
    style F fill:#8BC34A,color:#fff
    style G fill:#4CAF50,color:#fff
```

### Technique Impact Summary

| Technique             | Category       | Approx. Score Impact | Risk if Missing                  |
| --------------------- | -------------- | :------------------: | -------------------------------- |
| Real Chrome via CDP   | Identity       |       **+0.2**       | Instant `0.1` score (detected)   |
| Fingerprint Replay    | Identity       |       **+0.1**       | Inconsistency flags              |
| playwright-stealth    | Identity       |       **+0.1**       | `webdriver=true` detection       |
| Extended JS Injection | Identity       |      **+0.05**       | Minor inconsistency flags        |
| Human Behavior Sim    | Behavioral     |     **+0.1–0.2**     | Bot-like interaction pattern     |
| Google Warm-Up        | Session        |     **+0.1–0.3**     | No trusted session context       |
| Persistent Profile    | Session        |    **+0.05–0.1**     | Cold session penalty             |
| Token Interception    | Data           |       **N/A**        | _Capture mechanism, not scoring_ |
| Proxy Support         | Infrastructure |      **Varies**      | IP reputation dependent          |
| Process Hygiene       | Infrastructure |       **N/A**        | _Reliability, not scoring_       |

> **Note:** These are empirical estimates from testing. Actual impact varies based on IP reputation, time of day, target site configuration, and Google's evolving detection algorithms.

### Key Insight: Defense in Depth

No single technique achieves a high score alone. The system's strength comes from the **combination** of all techniques working together, creating a browser session that is indistinguishable from a real human user across every detection vector that reCAPTCHA v3 examines.
