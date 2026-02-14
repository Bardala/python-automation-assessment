# Task 3: DOM Scraping Assessment

This folder contains the solution for the DOM scraping assessment. The challenge was to scrape a captcha page that contains a large number of hidden images and instructions, extracting only the specific visible ones displayed to the user.

## Algorithm Description

The solution typically requires a hybrid approach because the target page uses JavaScript to dynamically manipulate the DOM, hiding most elements but keeping them in the source or stacking them.

### 1. Hybrid Scraping Strategy
To meet the requirement of scraping **all** images (including hidden ones) and **only visible** images, the script uses two different methods:

-   **Raw HTML Parsing (Requests + BeautifulSoup)**:
    -   **Goal**: Extract all 50+ images present in the page source.
    -   **Method**: Fetches the raw HTML response before JavaScript executes. This ensures we capture every `<img>` tag effectively.

-   **Live DOM Interaction (Playwright)**:
    -   **Goal**: Extract exactly the 9 visible images in the 3x3 grid and the single visible instruction.
    -   **Method**: Launches a real browser instance to render the page and execute JavaScript.

### 2. Visibility Logic (Z-Index Filtering)
A key challenge was that the "hidden" images and instructions were not hidden using standard CSS properties like `display: none` or `visibility: hidden`. Instead, they were **stacked on top of each other** at the same screen coordinates.

The script implements a robust filtering logic to identify the truly visible elements:
1.  **Grouping**: It groups all candidate images by their screen position (x, y coordinates).
2.  **Filtering**: For each position, it compares the `z-index` CSS property of all candidates.
3.  **Selection**: The element with the **highest z-index** is selected as the visible one.

This same logic is applied to the instruction text (`.box-label`), ensuring we extract the
This repository contains a professional implementation of a DOM scraping solution for a captcha challenge.

## Project Structure

```
task3-dom-scraping/
│
├── src/                # Core scraping implementation logic
│   └── scraper.py
├── outputs/            # Generated results (JSON/TXT)
│   ├── allimages.json
│   ├── visible_images_only.json
│   └── visible_instruction.txt
├── docs/               # Documentation & Security Analysis
│   └── task3_security_analysis.md
├── tools/              # Debugging & Verification utilities
│   └── verify_visibility.py
├── run.py              # Main entrypoint script
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

## Setup & Usage

### 1. Environment Setup

It is recommended to use a virtual environment to isolate dependencies and avoid conflicts.

#### Linux / macOS
```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install dependencies and browser
pip install -r requirements.txt
playwright install chromium
```

#### Windows
```powershell
# Create virtual environment
python -m venv .venv

# Activate environment
.venv\Scripts\activate

# Install dependencies and browser
pip install -r requirements.txt
playwright install chromium
```

### 2. Run the Scraper

**Headless Mode (Default):**
```bash
python run.py
```

**Headed Mode (Visual Verification):**
```bash
python run.py --headed
```

3.  **Verify Results**
    Check the `outputs/` directory for the generated files:
    - `allimages.json`: ~54 items (Raw HTML scrape)
    - `visible_images_only.json`: Exactly 9 items (Visible grid)
    - `visible_instruction.txt`: Single visible instruction

## Outputs

The script generates three files in this directory:

1.  **`allimages.json`**:
    -   Contains base64 data for **all** images found in the raw HTML (typically ~54+).
    -   *Source: Raw HTML Scraping*

2.  **`visible_images_only.json`**:
    -   Contains base64 data for **exactly 9** images corresponding to the visible 3x3 grid.
    -   *Source: Playwright + Z-Index Filtering*

3.  **`visible_instruction.txt`**:
    -   Contains the single line of text for the current instruction (e.g., "Please select all boxes with number 739").
    -   *Source: Playwright + Z-Index Filtering*
