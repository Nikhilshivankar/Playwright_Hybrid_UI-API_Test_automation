# Enterprise Hybrid Test Automation Framework (UI & API)

This repository contains a production-ready, enterprise-grade test automation framework built using **Python**, **Playwright**, and **Pytest**. It is structured to support both **End-to-End UI browser testing** (using the Page Object Model pattern) and **Backend API testing** (using Playwright's native fast HTTP request contexts). It features validated configurations, robust file logging, externalized test data, dual-reporting (JSON + Allure), and automated CI/CD pipelines via GitHub Actions.

---

## 🛠️ Framework Architecture

```text
Playwright_Hybrid_UI-API_Test_automation/
├── .github/
│   └── workflows/
│       └── playwright.yml         # CI/CD pipeline automation
├── api/
│   ├── definitions/              # API Client / Controller definitions (e.g. PetstoreClient)
│   │   ├── __init__.py
│   │   └── petstore_client.py
│   ├── models/                   # Pydantic models for serialization and validation
│   │   ├── __init__.py
│   │   ├── request_models.py     # API request schemas
│   │   └── response_models.py    # API response schemas
│   ├── specs/                    # Swagger / OpenAPI specification schemas
│   │   └── swagger.json
│   └── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py               # Dotenv/Pydantic-based configuration management
├── data/
│   └── test_data.json            # Externalized test suite parameters (UI & API)
├── pages/
│   ├── __init__.py
│   ├── base_page.py              # Custom resilient wrappers over Playwright API
│   └── login_page.py             # Login Page Object implementation
├── reports/                      # Auto-generated outputs (logs, screenshots, database)
│   ├── screenshots/              # Failure screenshots (UI only)
│   ├── allure-results/           # Raw allure results (UI & API)
│   ├── report.json               # JSON execution report
│   ├── run.log                   # Framework-wide log entries
│   └── test_database.db          # SQLite local test database instance
├── tests/
│   ├── api/                      # API endpoint test cases (using api/ layer)
│   │   ├── __init__.py
│   │   ├── test_auth.py          # Authentication tests (login, logout)
│   │   ├── test_pet.py           # Pet CRUD and DB validation tests
│   │   └── test_store.py         # Order placement and deletion tests
│   ├── ui/                       # UI browser-based test cases (using pages/ layer)
│   │   ├── __init__.py
│   │   └── test_login.py
│   ├── conftest.py               # Shared pytest fixtures, API contexts, and failure hooks
│   └── __init__.py
├── utils/
│   ├── __init__.py
│   ├── db_helper.py              # SQL Database connection and verification helper
│   └── logger.py                 # Custom logger configuration
├── .env.example                  # Environment configuration template
├── .gitignore                    # Project exclusions
├── pytest.ini                    # Core test-runner configurations
└── requirements.txt              # Standardized dependencies
```

### Key Engineering Pillars
1. **Separation of Concerns:** Test logic (`tests/`) is isolated from element selectors and page actions (`pages/`), configurations (`config/`), and data payloads (`data/`).
2. **Unified Testing Capabilities:** Runs full browser workflows alongside rapid API endpoint tests in the same suite.
3. **Robust Configuration:** Pydantic-based settings manager validates types and automatically reads configuration options from local `.env` files or system environment variables.
4. **Resilient Element Manipulation:** The `BasePage` wraps Playwright's default API to provide explicit waits, element logging, error catching, and debug steps.
5. **Smart Failure Capture:** The `pytest_runtest_makereport` hook captures screenshot logs upon UI test failures and links them immediately to Allure attachments.
6. **Traceability:** Logs (both browser interactions and API requests/responses) are written in real-time to both the standard terminal output and a rolling `reports/run.log` log file.
7. **Integrated Database Validation:** Exposes a SQL `DatabaseHelper` instance via pytest fixtures, facilitating automatic verification of backend writes and synchronization logic directly against database records during test steps.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have **Python 3.10+** and `pip` installed on your machine.

### 2. Set Up Virtual Environment
Create and activate a virtual environment to manage dependencies locally:

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install all package requirements, then trigger the Playwright driver installer to fetch standard browser binaries (Chromium, Firefox, Webkit) and system dependencies:
```bash
pip install -r requirements.txt
playwright install --with-deps chromium
```

### 4. Configuration Setup
Create a `.env` file by copying the template file:
```bash
cp .env.example .env
```
Customize the values inside `.env` to match your target site and browser execution options:
```ini
BASE_URL=https://practicetestautomation.com
BROWSER=chromium
HEADLESS=true
SLOW_MO=0
DEFAULT_TIMEOUT=30000
ENVIRONMENT=staging
LOG_LEVEL=INFO
```

---

## 🧪 Running Tests

You can run the entire test suite or target specific sets of tests.

### Run All Tests
To run all tests in the framework:
```bash
pytest
```

### Run in Headed Mode
To override the default headless option and watch test runs in the browser:
```bash
pytest --headed
```

### Run by Pytest Marker
Run only tests marked with a specific tag (defined in `pytest.ini`):
```bash
# Run smoke tests
pytest -m smoke

# Run regression tests
pytest -m regression

# Run API tests only
pytest -m api
```

### Run on a Specific Browser
Select which browser to use (Chromium, Firefox, or Webkit):
```bash
pytest --browser firefox
```

---

## 📊 Reports & Logging

This framework provides multiple reporting outputs to support local debugging and CI execution:

### 1. File Logger
Logs are formatted and piped to `reports/run.log`. It lists exact navigation links, element clicks, API requests, response codes, and assertions.
```text
2026-06-26 20:30:04 [    INFO] API POST Request -> https://petstore.swagger.io/v2/pet (petstore_client.py:24)
2026-06-26 20:30:05 [    INFO] API POST Response Status: 200 (petstore_client.py:28)
2026-06-26 20:30:05 [    INFO] --- Execution Started: test_login_successful --- (test_login.py:19)
2026-06-26 20:30:05 [    INFO] Navigating to URL: https://practicetestautomation.com/practice-test-login/ (base_page.py:18)
2026-06-26 20:30:15 [    INFO] Entering value into 'Username Input': student (base_page.py:32)
```

### 2. JSON Reports
A machine-readable JSON report is generated at `reports/report.json` via `pytest-json-report`. This is useful for passing test results to custom dashboards, Slack notifications, or database tracking.

### 3. Allure Reporting
Allure produces comprehensive, interactive HTML reports with screenshots, environment details, execution steps, and trends.

To view Allure reports locally:
1. Install Allure CLI:
   * **Windows (via Scoop):** `scoop install allure`
   * **macOS (via Homebrew):** `brew install allure`
2. Serve and compile the raw files under the output directory:
   ```bash
   allure serve reports/allure-results
   ```

---

## 🔄 GitHub Actions CI/CD Integration

The CI/CD pipeline configuration is located in [playwright.yml](file:///.github/workflows/playwright.yml).

The pipeline automatically triggers on pushes or pull requests to the `main`, `master`, or `dev` branches. 

### GitHub Pipeline Phases
1. **Environment Setup:** Spins up an Ubuntu runner and sets up Python `3.11` using pip caching.
2. **Installation:** Resolves package requirements and pulls Playwright browser dependencies.
3. **Execution:** Runs the test suites.
4. **Artifact Archiving:** Uploads the entire `reports/` folder (including failure screenshots, logs, and Allure results) back to the GitHub workflow run.
