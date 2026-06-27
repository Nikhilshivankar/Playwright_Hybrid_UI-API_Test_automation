# Framework Design Interview Q&A (Playwright Hybrid Framework)

This document contains potential interview questions and answers based on the architecture and implementation of this Playwright Hybrid UI & API Test Automation framework. It serves as an excellent study guide for automation engineering interviews.

---

## 1. Framework Architecture & Design

**Q: Can you explain the architecture of your test automation framework?**
**A:** This is a Hybrid Test Automation framework built using Python, Playwright, and Pytest. It supports both UI and API testing within the same project ecosystem. 
Key architectural components include:
- **`pages/`**: Implements the Page Object Model (POM) for UI components.
- **`api/`**: Contains API wrappers and request managers (`petstore_client.py`).
- **`tests/`**: Contains the actual Pytest test scripts (separated into `ui`, `api`, and `e2e` directories).
- **`utils/`**: Helper functions, custom loggers, and shared utilities.
- **`data/`**: Test data files (JSON) used for parameterization and Data-Driven Testing.
- **`config/`**: Configuration management using `pydantic-settings` to securely load environments and secrets.
- **`reports/`**: Destination for generated custom HTML reports, screenshots, and logs.

**Q: Why did you choose Playwright over Selenium or Cypress?**
**A:** Playwright offers several major advantages for modern web testing:
1. **Auto-waiting**: It automatically waits for elements to be actionable (visible, enabled, stable) before interacting, drastically reducing flaky tests.
2. **Built-in API Testing**: It provides an `APIRequestContext` which allows us to perform backend API testing without importing external libraries like `requests`.
3. **Cross-browser & Multi-context**: It supports Chromium, Firefox, and WebKit natively. It also allows multiple browser contexts (incognito-like sessions) in a single test, which is great for multi-user scenarios.
4. **Speed**: Playwright communicates directly with the browser via WebSocket protocols, making it significantly faster than Selenium's WebDriver HTTP overhead.

---

## 2. Page Object Model (POM)

**Q: How did you implement the Page Object Model in this framework?**
**A:** We created separate classes for each web page in the `pages/` directory. Each class encapsulates the Playwright locators (e.g., `page.locator(...)`) and the actions/methods (e.g., `login(username, password)`) that can be performed on that page. Tests instantiate these page objects, keeping the test scripts clean, readable, and maintaining locators in a single centralized location for easy updates if the UI changes.

**Q: How do you handle dynamic web elements?**
**A:** We prioritize resilient locators. Playwright encourages using user-facing attributes like role, text, or test-ids (`page.get_by_role()`, `page.get_by_test_id()`). If an ID is dynamic, we avoid it entirely and instead locate elements by their semantic meaning or hierarchy, ensuring the test mimics how a real user finds the element.

---

## 3. UI and API Integration

**Q: How do you handle scenarios that require both UI and API interactions?**
**A:** Playwright provides both a `page` fixture for UI and a `request` (`APIRequestContext`) fixture for API calls. In our framework, we can seamlessly use both in an End-to-End (E2E) test. For example, we might create test data via an API POST request (which is fast and reliable) and then use the UI to verify that the data appears correctly on the frontend. We can also use the API to fetch a session token and inject it into the browser context to bypass the UI login screen entirely.

**Q: How are you validating the API responses?**
**A:** We use **Pydantic** models to validate API payloads and responses. Instead of manually parsing JSON dictionaries, we feed the JSON response directly into a Pydantic `BaseModel`. If the API schema changes (e.g., a required field is missing or data types don't match), Pydantic immediately throws a `ValidationError`, ensuring strict contract testing.

---

## 4. Pytest & Fixtures

**Q: What is the purpose of `conftest.py`?**
**A:** `conftest.py` is a special Pytest file where we define shared fixtures, hooks, and plugins. Any fixture defined in `conftest.py` is automatically available to all tests in the directory structure without needing to be imported. We use it to set up our browser contexts, instantiate Page Objects (`login_page`), configure loggers, and format the HTML report.

**Q: What are fixture scopes in Pytest? Which ones do you use?**
**A:** Scopes determine how often a fixture is invoked:
- **`function`** (default): Runs once per test. We use this for our `page` and Page Object fixtures to ensure every test starts with a clean slate.
- **`session`**: Runs once per test suite execution. We use this for high-level setup, like generating a global timestamp for the report folder or establishing a global database connection.
- **`module`**: Runs once per test file.
- **`class`**: Runs once per test class.

---

## 5. Configuration, Secrets, and Security

**Q: How do you manage different test environments and secure credentials?**
**A:** Security and environment management are handled via `config/settings.py` using `pydantic-settings`. 
- **No Hardcoded Secrets**: All passwords and keys are stripped from source code and JSON files.
- **.env Files**: Locally, we use a git-ignored `.env` file to store credentials. Pydantic automatically loads these into strongly-typed variables (`settings.TEST_USERNAME`).
- **GitHub Secrets**: In our CI/CD pipeline, these variables are securely injected into the runtime environment via GitHub Repository Secrets and Variables. If a required secret is missing, Pydantic fails fast upon instantiation rather than failing mysteriously mid-test.

---

## 6. Test Data Management

**Q: How do you achieve Data-Driven Testing?**
**A:** We store test data externally in the `data/` directory as JSON files. In Pytest, we can use `@pytest.mark.parametrize` to feed different data sets (e.g., multiple invalid login combinations) into a single test function. The test function is executed multiple times automatically, reducing code duplication.

---

## 7. Reporting and Metrics

**Q: What reporting tools are you using, and how do you track Test Cases?**
**A:** We use `pytest-html` to generate interactive HTML reports. We heavily customized this report using Pytest hooks (`pytest_html_results_table_header`, `pytest_runtest_makereport`).
- **Custom Dashboard**: We inject a custom CSS/JS Metrics Dashboard at the top of the report to calculate UI vs API pass rates automatically based on Pytest markers (`@pytest.mark.ui`).
- **Test Case IDs**: We created a custom `@pytest.mark.tc_id("TC_001")` marker. Our hooks extract this marker at runtime and dynamically inject a **TC ID** column into the HTML report table, allowing easy mapping to Jira or TestRail.

---

## 8. Continuous Integration (CI/CD)

**Q: How are these tests executed in your CI/CD pipeline?**
**A:** We use GitHub Actions (`.github/workflows/pipeline_runner.yml`). The workflow triggers on pushes or pull requests. It provisions an Ubuntu runner, sets up Python, installs dependencies and Playwright binaries, injects secure Environment Variables, and runs `pytest`. Finally, it archives the generated HTML report as a pipeline artifact (using `actions/upload-artifact`) regardless of whether the tests passed or failed, ensuring we always have access to the logs.

---

## 9. Parallel Execution & Performance

**Q: How do you speed up the test execution time?**
**A:** We use the `pytest-xdist` plugin to run tests in parallel. Tests are specifically designed to be atomic and independent (no shared state, unique test data). Because of this, `pytest -n auto` can distribute the tests concurrently across multiple CPU workers, drastically reducing the overall execution time.

---

## 10. Error Handling and Debugging

**Q: What happens when a test fails? How do you debug it?**
**A:** 
1. **Screenshots/Traces**: Playwright is configured in `conftest.py` to automatically capture full-page screenshots upon test failure. These are encoded into Base64 and embedded directly into the Pytest-HTML report.
2. **Logging**: We have a custom global logger (using Python's `logging` module) that logs every major action (e.g., "Navigating to URL", "Clicking Submit"). This log stream is attached to the report for every individual test.
3. **Playwright UI Mode**: For local debugging, we can run `pytest --ui` to open Playwright's time-travel debugger, which lets us step through the DOM state, network calls, and console logs at every exact millisecond of the test execution.

---

## 11. Locators and Assertions

**Q: What is your strategy for locating elements, and how do you handle assertions?**
**A:** Our strategy strictly avoids fragile locators like XPath or absolute CSS selectors. Instead, we use Playwright's built-in robust locators (e.g., `get_by_role`, `get_by_test_id`, `get_by_text`). This ensures tests mimic real user behavior and remain resilient against DOM changes.
For assertions, we use Python's native `assert` keyword paired with our Page Object Model methods (e.g., `assert login_page.is_success_header_displayed()`). Because Playwright auto-waits for elements to become visible and stable under the hood before returning boolean values, standard Python assertions work flawlessly without needing manual `time.sleep()` or explicit wait loops.

---

## 12. Cross-Browser & Mobile Emulation Testing

**Q: Does your framework support cross-browser testing?**
**A:** Yes. Playwright natively bundles Chromium, Firefox, and WebKit (Safari). In our `pipeline_runner.yml`, we can easily pass environment variables (`BROWSER=firefox`) to dictate which browser engine the Pytest suite should use. Playwright also supports mobile emulation, allowing us to simulate specific devices (like an iPhone 13 or Pixel 5) by configuring the browser context viewport and user agent directly in `conftest.py`.

---

## 13. Advanced Playwright Features (Mocking & Interception)

**Q: Have you used Network Interception or API Mocking in Playwright?**
**A:** Yes, Playwright allows us to intercept network traffic using `page.route()`. This is an advanced and incredibly useful feature for:
1. **Mocking 3rd-party APIs**: If a backend service is down, we can mock the JSON response so the UI tests can still run.
2. **Simulating Edge Cases**: We can force a 500 Server Error or delay a response by 5 seconds to verify how the frontend UI handles loading spinners and error banners.
3. **Blocking Resources**: We can block heavy images or analytics scripts from loading to drastically speed up E2E test execution.

---

## 14. Golden Principles of Framework Design

**Q: What are the core principles of designing a test automation framework, and how did you apply them here?**
**A:** Designing a robust framework requires adhering to several core principles:

1. **Maintainability (Separation of Concerns)**: We use the **Page Object Model (POM)** so that UI selectors and actions are separated from test scripts. If the UI changes, we only update one Page class, not 50 tests.
2. **Reusability (DRY)**: We avoid copying and pasting setup code by utilizing **Pytest Fixtures**. Things like browser initialization, authentication, and API clients are initialized once in `conftest.py` and reused everywhere.
3. **Scalability**: We configured the framework to support **Parallel Execution** (`pytest-xdist`), meaning as the test suite grows, we can scale execution across multiple CPU cores without tests interfering with each other.
4. **Independence (Atomic Tests)**: Tests should never rely on the execution order or left-over state from previous tests. Every test gets a clean slate (clean browser context).
5. **Reliability (Anti-Flakiness)**: We avoid hardcoded `time.sleep()` completely, instead leveraging Playwright's **Auto-waiting** mechanisms.
6. **Data-Driven Design**: Test logic is separated from test data. We store data in JSON files and use `@pytest.mark.parametrize` to run tests dynamically.
7. **Environment Abstraction**: Hardcoding URLs or credentials is a bad practice. The framework adapts to QA or Staging environments automatically using GitHub Secrets and `pydantic-settings` (`.env`).
8. **Visibility (Reporting & Logging)**: When a test fails in CI/CD, we generate detailed Pytest-HTML reports with Base64 embedded screenshots, stack traces, and custom logging streams.
9. **CI/CD Integration**: The framework is completely integrated into a **GitHub Actions** pipeline, automatically triggering tests on Pull Requests and Pushes.
