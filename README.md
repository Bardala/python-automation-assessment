# Web Scraping & Automation Project

This project uses Python with **Playwright** and **Pytest** for web scraping and automation.

## Setup Instructions

### 1. Install System Dependencies (Ubuntu)
Ensure the virtual environment module is installed:
```bash
sudo apt update
sudo apt install -y python3-venv
```

### 2. Initialize Virtual Environment
Create and activate a virtual environment to isolate dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Project Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
Download the necessary browser binaries:
```bash
playwright install
```

## Running Tests
Run the sample tests using Pytest:
```bash
pytest
```

To run in headed mode (see the browser):
```bash
pytest --headed
```

## Project Structure
- `test_example.py`: Sample Playwright test.
- `requirements.txt`: Project dependencies.
- `.gitignore`: Files and directories to be ignored by Git.
