# 🏗️ Project Architecture — `task1-recaptcha-stealth`

> A stealth reCAPTCHA v3 automation system built on Playwright + CDP, featuring
> real fingerprint replay, human behavior simulation, and async parallel execution.

---

## Table of Contents

1. [High-Level Overview](#1-high-level-overview)
2. [Directory Structure](#2-directory-structure)
3. [File Dependency Graph](#3-file-dependency-graph)
4. [Layered Architecture](#4-layered-architecture)
5. [Core Module Breakdown](#5-core-module-breakdown)
6. [Execution Modes](#6-execution-modes)
7. [Data Flow](#7-data-flow)
8. [Configuration System](#8-configuration-system)
9. [Helpers vs Root `src/` Modules](#9-helpers-vs-root-src-modules)

---

## 1. High-Level Overview

```mermaid
graph TB
    subgraph "🎯 Entry Points"
        A["src/main.py<br/><i>Single Run</i>"]
        B["scale_test.py<br/><i>Sequential Scale</i>"]
        C["scale_test_tabs.py<br/><i>Tab-Based Scale</i>"]
        D["scale_test_context.py<br/><i>Context-Based Scale</i>"]
        E["scale_test_async.py<br/><i>Async Parallel</i>"]
        F["diagnose.py<br/><i>Manual Diagnostic</i>"]
        G["record_fingerprint.py<br/><i>Fingerprint Capture</i>"]
    end

    subgraph "⚙️ Core Engine"
        H["src/core.py<br/><i>SSOT Business Logic</i>"]
    end

    subgraph "🛡️ Stealth Layer"
        I["src/stealth.py<br/><i>Sync Browser Launch</i>"]
        J["src/helpers/stealth.py<br/><i>Shared Stealth Utilities</i>"]
    end

    subgraph "🤖 Human Simulation"
        K["src/human.py<br/><i>Sync Mouse/Scroll</i>"]
        L["src/helpers/async_human.py<br/><i>Async Mouse/Scroll</i>"]
    end

    subgraph "📡 Data Extraction"
        M["src/interceptor.py<br/><i>Token Capture</i>"]
        N["src/extractor.py<br/><i>Score Parser</i>"]
    end

    subgraph "🔧 Config"
        O["config/settings.py<br/><i>URLs, Paths, Timeouts</i>"]
        P["config/logging_config.py<br/><i>Rotating File Logger</i>"]
    end

    A --> H
    B --> I
    C --> H
    D --> H
    E --> Q["src/async_manager.py"]
    Q --> J
    E --> R["src/async_worker.py"]
    R --> J
    R --> L
    H --> K
    H --> M
    H --> N
    I --> J
    J --> O
    O --> P
```

The system is designed around a **Single Source of Truth (SSOT)** pattern: `src/core.py` contains the core reCAPTCHA solving logic, and multiple entry points (runners) wrap that logic with different execution strategies (single, sequential, tab-based, context-based, async parallel).

---

## 2. Directory Structure

```
task1-recaptcha-stealth/
│
├── config/                          # 🔧 Configuration Layer
│   ├── __init__.py                  #    Package marker
│   ├── settings.py                  #    Global constants (URLs, paths, timeouts)
│   └── logging_config.py            #    Rotating file + console logger
│
├── src/                             # ⚙️ Application Source Code
│   ├── __init__.py                  #    Exports: run()
│   ├── __main__.py                  #    `python -m src` entry point
│   ├── main.py                      #    Single-run entry point with CLI args
│   ├── core.py                      #    ★ SSOT: solve_recaptcha() orchestrator
│   ├── stealth.py                   #    Sync stealth browser launcher (CDP)
│   ├── human.py                     #    Sync human behavior simulation
│   ├── async_human.py               #    Async human behavior simulation
│   ├── interceptor.py               #    Token capture via route interception
│   ├── extractor.py                 #    JSON response parser
│   ├── async_manager.py             #    Async browser lifecycle (Singleton)
│   ├── async_worker.py              #    Async per-iteration test worker
│   │
│   └── helpers/                     # 🧩 Shared Utility Modules (used by async path)
│       ├── __init__.py              #    Package marker
│       ├── stealth.py               #    Stealth utilities (shared by sync + async)
│       ├── human.py                 #    Sync human behavior (mirror of src/human.py)
│       ├── async_human.py           #    Async human behavior (mirror of src/async_human.py)
│       ├── interceptor.py           #    Token interceptor (mirror of src/interceptor.py)
│       ├── extractor.py             #    Score extractor (mirror of src/extractor.py)
│       └── outputs/                 #    (Reserved for helper-specific outputs)
│
├── outputs/                         # 📊 Runtime Outputs
│   ├── fingerprint.json             #    Recorded real browser fingerprint
│   ├── automation.log               #    Rotating log file
│   ├── results_async.json           #    Async test results
│   └── result_single_*.json         #    Individual single-run results
│
├── docs/                            # 📚 Documentation
│   ├── architecture.md              #    ★ This file
│   ├── stealth_strategy.md          #    Stealth techniques documentation
│   ├── Q1-score-parameters.md       #    reCAPTCHA scoring parameter analysis
│   ├── Q2-research.md               #    Research notes
│   └── step2-extraction.md          #    Data extraction documentation
│
├── .chrome_profile/                 # 🌐 Persistent Chrome user profile (gitignored)
├── .venv/                           # 🐍 Python virtual environment
│
├── record_fingerprint.py            # 🔍 Standalone: captures real browser fingerprint
├── scale_test.py                    # 🔁 Sequential scaled test runner
├── scale_test_tabs.py               # 🔁 Tab-based scaled test runner
├── scale_test_context.py            # 🔁 Context-based scaled test runner
├── scale_test_async.py              # ⚡ Async parallel test runner
├── diagnose.py                      # 🩺 Manual diagnostic tool
├── proxies.txt                      # 🔒 Proxy server list
├── requirements.txt                 # 📦 Python dependencies
└── README.md                        # 📖 Project overview
```

---

## 3. File Dependency Graph

### 3.1 — Sync Execution Path (Single Run)

```mermaid
graph LR
    subgraph "Entry"
        main["src/main.py"]
    end

    subgraph "Core"
        core["src/core.py"]
    end

    subgraph "Stealth"
        stealth["src/stealth.py"]
    end

    subgraph "Human Sim"
        human["src/human.py"]
    end

    subgraph "Data"
        interceptor["src/interceptor.py"]
        extractor["src/extractor.py"]
    end

    subgraph "Config"
        settings["config/settings.py"]
    end

    subgraph "Outputs"
        fp["outputs/fingerprint.json"]
    end

    main -->|"solve_recaptcha()"| core
    main -->|"create_stealth_persistent()"| stealth
    main -->|"OUTPUT_DIR"| settings

    core -->|"random_mouse_movements(),<br/>random_scroll(),<br/>human_click()"| human
    core -->|"TokenInterceptor"| interceptor
    core -->|"parse_recaptcha_response()"| extractor
    core -->|"TARGET_URL,<br/>GOOGLE_URL"| settings

    stealth -->|"_load_fingerprint()"| fp
    stealth -->|"FINGERPRINT_PATH,<br/>PROFILE_DIR"| settings

    style main fill:#4CAF50,color:#fff
    style core fill:#FF9800,color:#fff
    style stealth fill:#9C27B0,color:#fff
    style settings fill:#607D8B,color:#fff
```

### 3.2 — Async Execution Path (Parallel)

```mermaid
graph LR
    subgraph "Entry"
        scaler["scale_test_async.py"]
    end

    subgraph "Async Engine"
        manager["src/async_manager.py"]
        worker["src/async_worker.py"]
    end

    subgraph "Shared Helpers"
        h_stealth["src/helpers/stealth.py"]
        h_async_human["src/helpers/async_human.py"]
        h_extractor["src/helpers/extractor.py"]
    end

    subgraph "Config"
        settings["config/settings.py"]
        logging["config/logging_config.py"]
    end

    scaler -->|"AsyncBrowserManager"| manager
    scaler -->|"run_async_test()"| worker
    scaler -->|"OUTPUT_DIR"| settings

    manager -->|"_find_chrome_binary(),<br/>_kill_existing_chrome(),<br/>_wait_for_port(),<br/>_load_fingerprint()"| h_stealth
    manager -->|"DEFAULT_DEBUG_PORT,<br/>PROFILE_DIR"| settings

    worker -->|"_build_stealth(),<br/>_extra_fingerprint_script(),<br/>_load_fingerprint()"| h_stealth
    worker -->|"random_mouse_movements(),<br/>random_scroll(),<br/>human_click()"| h_async_human
    worker -->|"parse_recaptcha_response()"| h_extractor
    worker -->|"TARGET_URL,<br/>GOOGLE_URL,<br/>NAV_TIMEOUT"| settings
    worker -->|"setup_logger()"| logging

    h_stealth -->|"FINGERPRINT_PATH,<br/>PROFILE_DIR"| settings

    style scaler fill:#2196F3,color:#fff
    style manager fill:#E91E63,color:#fff
    style worker fill:#FF5722,color:#fff
    style h_stealth fill:#9C27B0,color:#fff
    style settings fill:#607D8B,color:#fff
```

### 3.3 — Scale Test Runners Dependency Comparison

```mermaid
graph TD
    subgraph "Runners"
        ST["scale_test.py<br/><i>Sequential</i>"]
        STT["scale_test_tabs.py<br/><i>Tab-Based</i>"]
        STC["scale_test_context.py<br/><i>Context-Based</i>"]
        STA["scale_test_async.py<br/><i>Async Parallel</i>"]
    end

    subgraph "Sync Modules (src/)"
        core["core.py"]
        stealth["stealth.py"]
        main_mod["main.py"]
        human["human.py"]
        interceptor["interceptor.py"]
    end

    subgraph "Async Modules (src/)"
        async_mgr["async_manager.py"]
        async_wrk["async_worker.py"]
    end

    subgraph "Helpers (src/helpers/)"
        h_stealth["stealth.py"]
        h_async["async_human.py"]
        h_ext["extractor.py"]
    end

    ST -->|imports| stealth
    ST -->|imports| interceptor
    ST -->|imports| human
    ST -->|imports| main_mod

    STT -->|imports| core
    STT -->|imports| stealth
    STT -->|imports| main_mod

    STC -->|imports| core
    STC -->|imports| stealth
    STC -->|imports| main_mod

    STA -->|imports| async_mgr
    STA -->|imports| async_wrk

    async_mgr -->|imports| h_stealth
    async_wrk -->|imports| h_stealth
    async_wrk -->|imports| h_async
    async_wrk -->|imports| h_ext

    style ST fill:#8BC34A,color:#fff
    style STT fill:#CDDC39,color:#000
    style STC fill:#FFC107,color:#000
    style STA fill:#2196F3,color:#fff
    style core fill:#FF9800,color:#fff
```

### 3.4 — Complete Import Map (All Files)

The following table shows every file and its exact imports from within the project:

| **File**                     | **Imports From**                                                                                                                                                                                                                                                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/__init__.py`            | `src/main.py` → `run`                                                                                                                                                                                                                                                                                                                                              |
| `src/__main__.py`            | `src/main.py` → `main`                                                                                                                                                                                                                                                                                                                                             |
| `src/main.py`                | `config/settings.py` → `OUTPUT_DIR`; `src/core.py` → `solve_recaptcha`; `src/stealth.py` → `create_stealth_persistent`                                                                                                                                                                                                                                             |
| `src/core.py`                | `config/settings.py` → `GOOGLE_URL, TARGET_URL`; `src/human.py` → `random_mouse_movements, random_scroll, human_click`; `src/interceptor.py` → `TokenInterceptor`; `src/extractor.py` → `parse_recaptcha_response`                                                                                                                                                 |
| `src/stealth.py`             | `config/settings.py` (via inline paths); `outputs/fingerprint.json` (file read)                                                                                                                                                                                                                                                                                    |
| `src/human.py`               | _(no project imports — only `playwright`, `random`, `time`)_                                                                                                                                                                                                                                                                                                       |
| `src/async_human.py`         | _(no project imports — only `playwright`, `random`)_                                                                                                                                                                                                                                                                                                               |
| `src/interceptor.py`         | _(no project imports — only `re`, `playwright`)_                                                                                                                                                                                                                                                                                                                   |
| `src/extractor.py`           | _(no project imports — only `json`)_                                                                                                                                                                                                                                                                                                                               |
| `src/async_manager.py`       | `config/settings.py` → `DEFAULT_DEBUG_PORT, PROFILE_DIR`; `src/helpers/stealth.py` → `_find_chrome_binary, _kill_existing_chrome, _wait_for_port, _load_fingerprint`                                                                                                                                                                                               |
| `src/async_worker.py`        | `config/settings.py` → `TARGET_URL, GOOGLE_URL, NAV_TIMEOUT, WARMUP_TIMEOUT`; `config/logging_config.py` → `setup_logger`; `src/helpers/stealth.py` → `_build_stealth, _extra_fingerprint_script, _load_fingerprint`; `src/helpers/async_human.py` → `random_mouse_movements, random_scroll, human_click`; `src/helpers/extractor.py` → `parse_recaptcha_response` |
| `src/helpers/stealth.py`     | `config/settings.py` → `FINGERPRINT_PATH, PROFILE_DIR`                                                                                                                                                                                                                                                                                                             |
| `src/helpers/human.py`       | _(no project imports)_                                                                                                                                                                                                                                                                                                                                             |
| `src/helpers/async_human.py` | _(no project imports)_                                                                                                                                                                                                                                                                                                                                             |
| `src/helpers/interceptor.py` | _(no project imports)_                                                                                                                                                                                                                                                                                                                                             |
| `src/helpers/extractor.py`   | _(no project imports)_                                                                                                                                                                                                                                                                                                                                             |
| `scale_test.py`              | `src/main.py` → `TARGET_URL, OUTPUT_DIR, parse_recaptcha_response`; `src/stealth.py` → `create_stealth_persistent`; `src/interceptor.py` → `TokenInterceptor`; `src/human.py` → `random_mouse_movements, random_scroll, human_click`                                                                                                                               |
| `scale_test_tabs.py`         | `src/core.py` → `solve_recaptcha`; `src/stealth.py` → `create_stealth_persistent`; `src/main.py` → `OUTPUT_DIR, parse_recaptcha_response`                                                                                                                                                                                                                          |
| `scale_test_context.py`      | `src/core.py` → `solve_recaptcha`; `src/stealth.py` → `create_stealth_persistent, _load_fingerprint, _build_stealth, _extra_fingerprint_script`; `src/main.py` → `OUTPUT_DIR`                                                                                                                                                                                      |
| `scale_test_async.py`        | `config/settings.py` → `OUTPUT_DIR, CONCURRENCY_LIMIT`; `src/async_manager.py` → `AsyncBrowserManager`; `src/async_worker.py` → `run_async_test`                                                                                                                                                                                                                   |
| `diagnose.py`                | _(standalone — uses `playwright` and `playwright_stealth` directly)_                                                                                                                                                                                                                                                                                               |
| `record_fingerprint.py`      | _(standalone — built-in `http.server`, writes to `outputs/`)_                                                                                                                                                                                                                                                                                                      |
| `config/logging_config.py`   | `config/settings.py` → `OUTPUT_DIR, PROJECT_ROOT`                                                                                                                                                                                                                                                                                                                  |

---

## 4. Layered Architecture

```mermaid
graph TB
    subgraph "Layer 1 — Entry Points & Runners"
        direction LR
        L1A["src/main.py"]
        L1B["scale_test.py"]
        L1C["scale_test_tabs.py"]
        L1D["scale_test_context.py"]
        L1E["scale_test_async.py"]
        L1F["diagnose.py"]
        L1G["record_fingerprint.py"]
    end

    subgraph "Layer 2 — Orchestration"
        direction LR
        L2A["src/core.py<br/><i>solve_recaptcha()</i>"]
        L2B["src/async_manager.py<br/><i>AsyncBrowserManager</i>"]
        L2C["src/async_worker.py<br/><i>run_async_test()</i>"]
    end

    subgraph "Layer 3 — Capabilities"
        direction LR
        L3A["src/stealth.py<br/>src/helpers/stealth.py"]
        L3B["src/human.py<br/>src/helpers/async_human.py"]
        L3C["src/interceptor.py<br/>src/helpers/interceptor.py"]
        L3D["src/extractor.py<br/>src/helpers/extractor.py"]
    end

    subgraph "Layer 4 — Configuration & Data"
        direction LR
        L4A["config/settings.py"]
        L4B["config/logging_config.py"]
        L4C["outputs/fingerprint.json"]
        L4D["proxies.txt"]
    end

    L1A --> L2A
    L1B --> L3A
    L1C --> L2A
    L1D --> L2A
    L1E --> L2B
    L1E --> L2C

    L2A --> L3A
    L2A --> L3B
    L2A --> L3C
    L2A --> L3D
    L2B --> L3A
    L2C --> L3A
    L2C --> L3B
    L2C --> L3D

    L3A --> L4A
    L3A --> L4C
    L2B --> L4A
    L2C --> L4A
    L2C --> L4B

    style L2A fill:#FF9800,color:#fff,stroke-width:3px
    style L3A fill:#9C27B0,color:#fff
    style L4A fill:#607D8B,color:#fff
```

| Layer                       | Responsibility                                                                                                                       | Key Principle                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| **Layer 1 — Entry Points**  | User-facing CLI tools. Choose how to run (single, scale, async).                                                                     | No business logic — just orchestration wrappers.                              |
| **Layer 2 — Orchestration** | `core.py` is the SSOT for the solve flow. `async_manager.py` manages browser lifecycle. `async_worker.py` executes async iterations. | All test logic lives here; runners delegate to this layer.                    |
| **Layer 3 — Capabilities**  | Stealth browser launch, human simulation, token interception, JSON parsing.                                                          | Pure, focused modules. No knowledge of test flow.                             |
| **Layer 4 — Configuration** | Centralized constants, paths, logger setup, fingerprint data.                                                                        | Single source of truth for all settings; no hardcoded values in upper layers. |

---

## 5. Core Module Breakdown

### 5.1 `src/core.py` — The SSOT Orchestrator

This is the **most important file** in the project. It defines the canonical reCAPTCHA solving flow that all runners call:

```mermaid
sequenceDiagram
    participant Runner as Entry Point
    participant Core as core.py
    participant Interceptor as interceptor.py
    participant Human as human.py
    participant Extractor as extractor.py
    participant Page as Browser Page

    Runner->>Core: solve_recaptcha(page)

    Core->>Interceptor: interceptor.attach(page, TARGET_URL)
    Note over Interceptor: Registers route handler<br/>to capture POST token

    Core->>Page: goto(google.com)
    Core->>Human: random_mouse_movements(page, count=2)
    Note over Core: Warm-up phase builds<br/>trusted session context

    Core->>Page: goto(TARGET_URL)
    Core->>Human: random_mouse_movements(page, count=3)
    Core->>Human: random_scroll(page)
    Core->>Page: wait_for_timeout(2000-3500ms)
    Note over Core: Dwell time is critical<br/>for high v3 scores

    Core->>Human: human_click(page, "#btn")
    Core->>Page: wait_for_function(JSON in #out)
    Core->>Page: inner_text("#out")
    Core->>Extractor: parse_recaptcha_response(raw_json)

    Core-->>Runner: result {score, success, token, ...}
```

### 5.2 `src/stealth.py` — Browser Launch Pipeline

```mermaid
flowchart TD
    A["_load_fingerprint()"] --> B{"Fingerprint<br/>exists?"}
    B -->|Yes| C["Load from outputs/fingerprint.json"]
    B -->|No| D["Use hardcoded defaults"]

    C --> E["_kill_existing_chrome(debug_port)"]
    D --> E

    E --> F["Kill processes on port"]
    F --> G["Remove stale lock files"]
    G --> H["_find_chrome_binary()"]
    H --> I["Build chrome_args[]"]

    I --> J{"Proxy<br/>provided?"}
    J -->|Yes| K["Append --proxy-server"]
    J -->|No| L[Continue]
    K --> L

    L --> M{"Headless?"}
    M -->|Yes| N["Insert --headless=new"]
    M -->|No| O[Continue]
    N --> O

    O --> P["subprocess.Popen(chrome_args)"]
    P --> Q["_wait_for_port(debug_port)"]
    Q --> R["sync_playwright().start()"]
    R --> S["connect_over_cdp()"]
    S --> T["_build_stealth(fp)"]
    T --> U["apply_stealth_sync(context)"]
    U --> V["_extra_fingerprint_script(fp)"]
    V --> W["context.add_init_script()"]
    W --> X["Return (browser, page, pw, chrome_proc)"]

    style A fill:#9C27B0,color:#fff
    style P fill:#F44336,color:#fff
    style T fill:#E91E63,color:#fff
    style X fill:#4CAF50,color:#fff
```

### 5.3 `src/async_manager.py` — Singleton Browser Manager

```mermaid
classDiagram
    class AsyncBrowserManager {
        -_instance: AsyncBrowserManager
        -initialized: bool
        +browser: Browser
        +playwright: Playwright
        +chrome_proc: Popen
        +debug_port: int
        +fingerprint: dict
        +__new__() AsyncBrowserManager
        +start(headless, proxy_url) Browser
        +stop()
        -_create_proxy_auth_extension(proxy_url) str
    }

    class AsyncScaler {
        +count: int
        +concurrency: int
        +results: list
        +semaphore: Semaphore
        +browser_manager: AsyncBrowserManager
        +run()
        -_worker(iteration) dict
        -_load_proxies() list
        -_validate_proxy(proxy) bool
    }

    AsyncScaler --> AsyncBrowserManager : uses
    AsyncBrowserManager --> "src/helpers/stealth" : delegates to

    note for AsyncBrowserManager "Singleton Pattern:<br/>Only one Chrome process<br/>shared across all workers"
```

---

## 6. Execution Modes

The project supports **5 distinct execution modes**, each optimized for a different use case:

```mermaid
graph LR
    subgraph "Single Process"
        A["🟢 main.py<br/>1 browser, 1 page,<br/>1 solve"]
        B["🟡 scale_test.py<br/>N browsers,<br/>N solves (sequential)"]
        C["🔵 scale_test_tabs.py<br/>1 browser, N tabs,<br/>N solves (sequential)"]
        D["🟠 scale_test_context.py<br/>1 browser, N contexts,<br/>N solves (sequential)"]
    end

    subgraph "Multi-Worker"
        E["🔴 scale_test_async.py<br/>1 browser, N contexts,<br/>concurrent via semaphore"]
    end

    A -->|"Best for"| A1["Development<br/>&<br/>Debugging"]
    B -->|"Best for"| B1["Reliability Testing<br/>(clean state each run)"]
    C -->|"Best for"| C1["Speed<br/>(reuses session cookies)"]
    D -->|"Best for"| D1["Isolation + Speed<br/>(clean contexts,<br/>single browser)"]
    E -->|"Best for"| E1["Max Throughput<br/>(parallel execution)"]
```

| Mode              | File                    | Browser Instances | Strategy                           | Isolation                |
| ----------------- | ----------------------- | :---------------: | ---------------------------------- | ------------------------ |
| **Single**        | `main.py`               |         1         | One-shot run                       | Full                     |
| **Sequential**    | `scale_test.py`         | N (new each run)  | Launch → Solve → Kill → Repeat     | Full (slow)              |
| **Tab-Based**     | `scale_test_tabs.py`    |         1         | Reuse browser, cycle tabs          | Partial (shared cookies) |
| **Context-Based** | `scale_test_context.py` |         1         | Reuse browser, fresh contexts      | High (incognito-like)    |
| **Async**         | `scale_test_async.py`   |         1         | Concurrent contexts with semaphore | High + parallel          |

---

## 7. Data Flow

### 7.1 — Fingerprint Recording & Replay

```mermaid
flowchart LR
    subgraph "Phase 1: Record (One-Time)"
        A["👤 Real Chrome Browser"] -->|"Opens"| B["record_fingerprint.py<br/>HTTP Server :8787"]
        B -->|"Serves HTML with JS"| A
        A -->|"Collects fingerprint via JS APIs"| C["POST /save-fingerprint"]
        C -->|"Saves"| D["outputs/fingerprint.json"]
    end

    subgraph "Phase 2: Replay (Every Run)"
        D -->|"Read by"| E["stealth.py<br/>_load_fingerprint()"]
        E -->|"Configures"| F["_build_stealth(fp)"]
        E -->|"Generates JS"| G["_extra_fingerprint_script(fp)"]
        F -->|"Applies to context"| H["Playwright Context"]
        G -->|"init_script injection"| H
    end

    style D fill:#FF9800,color:#fff,stroke-width:3px
    style H fill:#4CAF50,color:#fff
```

### 7.2 — Token Capture & Score Extraction

```mermaid
flowchart LR
    A["Browser Page"] -->|"Click #btn triggers<br/>reCAPTCHA execute()"| B["grecaptcha.execute()"]
    B -->|"Returns token"| C["Page JS: fetch(TARGET_URL,<br/>FormData{token})"]
    C -->|"Intercepted by"| D["TokenInterceptor._handle_route()"]
    D -->|"Extracts via regex"| E["interceptor.token"]

    C -->|"Server responds with JSON"| F["Server: verify token<br/>via Google API"]
    F -->|"Renders in #out"| G["<pre id='out'><br/>{google_response: {score:...}}"]
    G -->|"Parsed by"| H["extractor.parse_recaptcha_response()"]
    H -->|"Returns"| I["{ score, success,<br/>action, hostname }"]

    style D fill:#E91E63,color:#fff
    style H fill:#2196F3,color:#fff
```

### 7.3 — Output File Generation

```mermaid
flowchart TD
    subgraph "Runners"
        A["main.py"]
        B["scale_test.py"]
        C["scale_test_tabs.py"]
        D["scale_test_context.py"]
        E["scale_test_async.py"]
    end

    subgraph "outputs/"
        F["result_single_*.json"]
        G["scaled_test_progress.json"]
        H["tab_test_progress.json<br/>results_tabs_*.json"]
        I["context_test_progress.json<br/>results_context_*.json"]
        J["results_async.json"]
        K["automation.log"]
    end

    A --> F
    B --> G
    C --> H
    D --> I
    E --> J
    E --> K

    style K fill:#607D8B,color:#fff
```

---

## 8. Configuration System

```mermaid
graph TD
    subgraph "config/settings.py"
        A["PROJECT_ROOT<br/>OUTPUT_DIR<br/>PROFILE_DIR<br/>FINGERPRINT_PATH"]
        B["TARGET_URL<br/>GOOGLE_URL"]
        C["DEFAULT_DEBUG_PORT<br/>CONCURRENCY_LIMIT"]
        D["NAV_TIMEOUT<br/>WARMUP_TIMEOUT<br/>EXTRACTION_TIMEOUT"]
        E["USER_AGENT_FALLBACK"]
    end

    subgraph "Consumers"
        F["src/core.py"]
        G["src/stealth.py"]
        H["src/helpers/stealth.py"]
        I["src/async_manager.py"]
        J["src/async_worker.py"]
        K["src/main.py"]
        L["config/logging_config.py"]
    end

    A --> G
    A --> H
    A --> I
    A --> K
    A --> L
    B --> F
    B --> J
    C --> I
    D --> J
    E -.->|"Fallback only"| G
    E -.->|"Fallback only"| H

    style A fill:#607D8B,color:#fff
    style B fill:#F44336,color:#fff
    style C fill:#9C27B0,color:#fff
```

All configuration values are **centralized** in `config/settings.py`. No module hardcodes URLs, paths, or timeouts. This makes the system easily configurable for different environments or target sites.

---

## 9. Helpers vs Root `src/` Modules

The project has **two copies** of several modules — one in `src/` and one in `src/helpers/`. This is a deliberate architectural choice:

```mermaid
graph TD
    subgraph "src/ (Root Modules)"
        A["stealth.py<br/><i>Self-contained paths</i>"]
        B["human.py<br/><i>Sync (time.sleep)</i>"]
        C["interceptor.py"]
        D["extractor.py"]
    end

    subgraph "src/helpers/ (Shared Modules)"
        E["stealth.py<br/><i>Uses config/settings.py</i>"]
        F["async_human.py<br/><i>Async (await)</i>"]
        G["interceptor.py"]
        H["extractor.py"]
    end

    subgraph "Used By"
        I["Sync Path:<br/>main.py, core.py,<br/>scale_test_*.py"]
        J["Async Path:<br/>async_manager.py,<br/>async_worker.py"]
    end

    A --> I
    B --> I
    C --> I
    D --> I

    E --> J
    F --> J
    G -.->|"Available but<br/>async_worker uses<br/>inline interception"| J
    H --> J

    style I fill:#4CAF50,color:#fff
    style J fill:#2196F3,color:#fff
```

| Aspect                | `src/` Root Modules                    | `src/helpers/` Modules                     |
| --------------------- | -------------------------------------- | ------------------------------------------ |
| **Path resolution**   | Uses `os.path` relative to `__file__`  | Uses `config/settings.py` constants        |
| **Async support**     | Sync only (`time.sleep()`)             | Both sync and async (`await`)              |
| **Primary consumers** | `main.py`, `core.py`, `scale_test*.py` | `async_manager.py`, `async_worker.py`      |
| **Design intent**     | Original modules for the sync pipeline | Refactored for the async/parallel pipeline |

> **Note:** `src/helpers/human.py` and `src/helpers/interceptor.py` are mirrors of their `src/` counterparts (identical code). `src/helpers/stealth.py` differs in that it imports paths from `config/settings.py` instead of computing them inline. `src/helpers/async_human.py` is a fully async version of `src/human.py`.
