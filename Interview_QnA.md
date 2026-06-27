# Test Automation Interview Q&A (Playwright Hybrid Framework)

This document contains potential interview questions and answers based on the architecture and implementation of this Playwright Hybrid UI & API Test Automation framework.

## 1. Framework Architecture & Design
**Q: Can you explain the architecture of your test automation framework?**
**A:** This is a Hybrid Test Automation framework built using Python, Playwright, and Pytest. It supports both UI and API testing within the same project. 
Key components include:
- **`pages/`**: Implements the Page Object Model (POM) for UI components.
- **`api/`**: Contains API request wrappers and handlers.
- **`tests/`**: Contains the actual Pytest test scripts (both UI and API).
- **`utils/`**: Helper functions, custom loggers, and shared utilities.
- **`data/`**: Test data files (JSON, CSV, etc.) for Data-Driven Testing.
- **`config/`**: Configuration management and environment settings.

## 2. Page Object Model (POM)
**Q: How did you implement the Page Object Model in this framework?**
**A:** We created separate classes for each web page in the `pages/` directory. Each class encapsulates the Playwright locators (e.g., `page.locator(...)`) and the actions/methods (e.g., `login(username, password)`) that can be performed on that page. Tests instantiate these page objects, keeping the test scripts clean and locators centralized for maintenance.

## 3. UI and API Integration
**Q: How do you handle scenarios that require both UI and API interactions?**
**A:** Playwright provides both a `page` fixture for UI and a `request` (APIRequestContext) fixture for API calls. In our tests, we can seamlessly use both. For example, we might create test data via an API POST request (fast and reliable) and then use the UI to verify that the data appears correctly on the frontend.

## 4. Configuration and Environment Management
**Q: How do you manage different test environments (e.g., QA, Staging, Prod)?**
**A:** We use `.env` files and a configuration manager (in `config/`). Environment variables like `BASE_URL`, credentials, and flags are loaded at runtime. In GitHub Actions, we pass these variables to dictate where the tests should run.

## 5. Test Data Management
**Q: How do you achieve Data-Driven Testing?**
**A:** We store test data externally in the `data/` directory (e.g., JSON files). In Pytest, we use `@pytest.mark.parametrize` along with custom functions to read these files, allowing us to run the same test function multiple times with different sets of inputs and expected outputs.

## 6. Reporting and Metrics
**Q: What reporting tools are you using, and how are metrics tracked?**
**A:** We use `pytest-html` to generate an interactive HTML report (`reports/report.html`). We also customized `tests/conftest.py` using pytest hooks (`pytest_runtest_logreport` and `pytest_html_results_summary`) to inject a custom Metrics Dashboard at the top of the report. This dashboard categorizes tests by tags (e.g., UI vs. API) and calculates pass/fail percentages automatically.

## 7. Continuous Integration (CI/CD)
**Q: How are these tests executed in your CI/CD pipeline?**
**A:** We use GitHub Actions (`.github/workflows/pipeline_runner.yml`). The workflow triggers on pushes or pull requests to `main`. It sets up Python, installs dependencies, installs Playwright browsers, and runs `pytest`. Finally, it archives the generated HTML report as a pipeline artifact regardless of whether the tests passed or failed.

## 8. Parallel Execution
**Q: How do you speed up the test execution time?**
**A:** We use the `pytest-xdist` plugin to run tests in parallel. Tests are designed to be independent (no shared state) so they can be executed concurrently across multiple CPU workers, drastically reducing the overall execution time.

## 9. Error Handling and Debugging
**Q: What happens when a test fails? How do you debug it?**
**A:** Playwright is configured to automatically capture screenshots, traces, or videos upon test failure. These artifacts are attached to the HTML report. In `pytest.ini` and `conftest.py`, we manage log levels and artifact collection to ensure we have maximum context (stack trace, DOM state, network calls) when debugging a flaky or failed test.

## 10. Test Case (TC) ID Mapping
**Q: How do you map or execute tests based on specific Test Case IDs (like TC_001, TC_002) from Jira/TestRail?**
**A:** There are a few ways we handle this in the Pytest framework:
1. **Naming Convention (Simplest):** We include the TC ID in the test function name (e.g., `def test_TC001_valid_login()`). This allows us to run specific tests easily from the command line using `pytest -k "TC001"`.
2. **Pytest Markers:** We can define custom markers (e.g., `@pytest.mark.tc001`) and run them using `pytest -m tc001`.
3. **Reporting Integration:** If using Allure, we use decorators like `@allure.id("TC_001")` or `@allure.testcase("https://jira.../TC_001", "TC_001")` to link the automated test directly back to the test management tool. For our custom `pytest-html` report, we can parse the TC ID from the function name or marker and display it in a dedicated column.
