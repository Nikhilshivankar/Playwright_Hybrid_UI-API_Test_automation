# Pytest Interview Questions and Answers

This document serves as a study guide for test automation interviews, focusing specifically on **Pytest** concepts, features, and best practices.

---

## 1. Pytest Basics & Comparisons

**Q: What is Pytest, and why is it preferred over Python's built-in `unittest` module?**
**A:** Pytest is a robust, third-party testing framework for Python. It is generally preferred over `unittest` because:
1. **Less Boilerplate**: Pytest doesn't require tests to be wrapped in classes or inherit from base classes. You can write simple functions (`def test_login()`).
2. **Native Assertions**: Pytest uses Python's standard `assert` keyword instead of cumbersome methods like `self.assertEqual()`. It uses advanced introspection to provide highly detailed failure messages.
3. **Powerful Fixtures**: Pytest features a highly modular and scalable fixture system (`conftest.py`) rather than relying on strict `setUp()` and `tearDown()` methods.
4. **Rich Plugin Ecosystem**: It has a massive ecosystem of plugins (e.g., `pytest-xdist` for parallel execution, `pytest-html` for reporting, `pytest-cov` for coverage).

---

## 2. Fixtures and Setup/Teardown

**Q: What are Pytest fixtures, and how do you use them?**
**A:** Fixtures are functions that run before (and optionally after) your test functions to set up a required state, initialize dependencies (like a database connection or a WebDriver), or inject test data. They are defined using the `@pytest.fixture` decorator and are injected into tests simply by adding the fixture name as an argument to the test function.

**Q: Explain fixture scopes. What scopes are available?**
**A:** Scopes determine how often a fixture is executed.
- **`function` (default)**: The fixture runs once for every test function that requests it.
- **`class`**: The fixture runs once per test class.
- **`module`**: The fixture runs once per test script (`.py` file).
- **`package`**: The fixture runs once per package (directory containing `__init__.py`).
- **`session`**: The fixture runs exactly once per test run execution (great for high-level setup like starting a server or configuring a global logger).

**Q: How do you handle teardown (cleanup) in Pytest fixtures?**
**A:** Teardown is handled using the `yield` keyword instead of `return`. The code before the `yield` statement acts as the setup, and the code after the `yield` statement acts as the teardown. The teardown executes after the test finishes, regardless of whether the test passed or failed.
```python
@pytest.fixture
def browser():
    # Setup
    driver = launch_browser()
    yield driver
    # Teardown
    driver.quit()
```

**Q: What is `conftest.py`?**
**A:** `conftest.py` is a special file used by Pytest to share fixtures, plugins, and hooks across multiple test files. Any fixture defined in `conftest.py` is automatically available to any test within that directory and its subdirectories, without needing an explicit `import` statement.

**Q: What does `autouse=True` do in a fixture?**
**A:** Setting `@pytest.fixture(autouse=True)` forces the fixture to run automatically for every test in its scope, even if the test does not explicitly request the fixture by name. It is useful for global setups like logging initialization or clearing browser cookies before every test.

**Q: How do you parameterize a fixture, and what is the `request` fixture?**
**A:** We parameterize a fixture using the `params` argument in the `@pytest.fixture(params=[...])` decorator. The fixture will execute once for each parameter value. Within the fixture, we access the current parameter using the built-in `request` fixture's `request.param` attribute.

**Example Code:**
```python
import pytest

@pytest.fixture(params=["mysql", "postgres"])
def db_client(request):
    db_type = request.param
    client = connect_to_db(db_type)
    yield client
    client.disconnect()

def test_db_query(db_client):
    assert db_client.is_connected()
```

---

## 3. Exception Testing & Assertions

**Q: How do you verify that a specific exception is raised in Pytest?**
**A:** We use the `pytest.raises` context manager. It asserts that a block of code raises a specific exception. If the exception is not raised, the test fails. We can also capture the exception details using `as exc_info` to inspect its message, type, or custom attributes.

**Example Code:**
```python
import pytest

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError) as exc_info:
        res = 1 / 0
    # Assert exception message contains expected text
    assert "division by zero" in str(exc_info.value)
```

**Q: How does Pytest handle assertion introspection, and how can you customize it?**
**A:** Pytest uses standard Python `assert` statements, but re-writes the AST (Abstract Syntax Tree) before compilation to capture the operands. This allows Pytest to show extremely detailed diffs and evaluations on failure (e.g., comparing lists or dicts). We can customize representations using the `pytest_assertrepr_compare` hook in `conftest.py` to print custom, clean messages for user-defined class comparisons.

---

## 4. Markers and Test Selection

**Q: What are Pytest Markers?**
**A:** Markers (`@pytest.mark.xyz`) are used to tag tests with specific metadata. You can use them to group tests logically, like `@pytest.mark.smoke`, `@pytest.mark.regression`, or `@pytest.mark.ui`. You can then run specific groups from the command line using the `-m` flag (e.g., `pytest -m smoke`).

**Q: How do you skip a test or mark it as a known failure?**
**A:** 
- **`@pytest.mark.skip(reason="...")`**: Completely skips the test execution.
- **`@pytest.mark.skipif(condition, reason="...")`**: Skips the test dynamically if a condition is met (e.g., `sys.platform == 'win32'`).
- **`@pytest.mark.xfail(reason="Known bug")`**: Runs the test, but expects it to fail. If it fails, it's marked as an "expected failure" (XFAIL) rather than a hard failure. If it unexpectedly passes, it is marked as an XPASS.

---

## 5. Parameterization / Data-Driven Testing

**Q: How do you perform Data-Driven Testing in Pytest?**
**A:** We use the `@pytest.mark.parametrize` decorator. It allows us to pass multiple sets of arguments to a single test function, effectively running the same test logic multiple times with different inputs.
```python
@pytest.mark.parametrize("username, password", [
    ("validUser", "validPass"),
    ("invalidUser", "validPass"),
    ("validUser", "invalidPass")
])
def test_login(username, password):
    # Test logic here...
```

---

## 6. Mocking and Monkeypatching

**Q: What is the `monkeypatch` fixture, and when should you use it?**
**A:** `monkeypatch` is a built-in Pytest fixture that allows you to temporarily modify classes, modules, dictionaries, environment variables, or `sys.path` during a test execution. Once the test finishes, Pytest automatically restores the original values, preventing state leakage (test pollution) to other tests.

**Example Code (Mocking Environment Variable & API call):**
```python
import os
import requests

def test_get_api_data(monkeypatch):
    # 1. Mocking an environment variable
    monkeypatch.setenv("API_KEY", "mock_key")
    
    # 2. Mocking a method of requests library
    class MockResponse:
        @staticmethod
        def json():
            return {"status": "success"}

    monkeypatch.setattr(requests, "get", lambda url: MockResponse())
    
    # Run assertions
    response = requests.get("https://api.example.com")
    assert response.json()["status"] == "success"
    assert os.getenv("API_KEY") == "mock_key"
```

**Q: What is `pytest-mock`, and why is it preferred over Python's built-in `unittest.mock.patch`?**
**A:** `pytest-mock` is a plugin that provides the `mocker` fixture. It is a thin wrapper around Python's standard `unittest.mock`. It is preferred because:
1. **No Decorator Nesting**: You don't need to write multiple `@mock.patch` decorators above your test functions.
2. **Automatic Cleanup**: Any patch or spy created using the `mocker` fixture is automatically undone at the end of the test.
3. **Clean Fixture Integration**: It can be used directly inside other custom fixtures.

**Example Code:**
```python
def test_user_service(mocker):
    # Mocking a method of a class
    mock_db = mocker.patch("app.database.UserDB.get_user")
    mock_db.return_value = {"id": 1, "name": "Alice"}
    
    # Call code that uses UserDB
    user = get_user_profile(user_id=1)
    assert user["name"] == "Alice"
    mock_db.assert_called_once_with(1)
```

---

## 7. Pytest Configuration

**Q: Where can you configure Pytest settings, and what are the main configuration files?**
**A:** Pytest configurations can be defined in `pytest.ini`, `pyproject.toml` (under `[tool.pytest.ini_options]`), `setup.cfg`, or `tox.ini`. `pytest.ini` is the primary and most common option.

**Example `pytest.ini` configuration:**
```ini
[pytest]
# Default command line arguments (verbose, short traceback)
addopts = -v --tb=short

# Restrict pytest to look for tests only in these directories
testpaths = tests

# Register custom markers to avoid warnings
markers =
    smoke: Quick smoke tests
    regression: Full regression suite
    ui: Web UI tests

# Configure rules to ignore or raise specific deprecation warnings
filterwarnings =
    ignore::DeprecationWarning
```

---

## 8. Command Line Execution

**Q: How do you run specific tests from the command line?**
**A:**
- Run a specific file: `pytest tests/test_login.py`
- Run a specific test function: `pytest tests/test_login.py::test_valid_login`
- Run by keyword matching: `pytest -k "login and not valid"` (Runs tests containing 'login' in the name, but not 'valid')
- Run by marker: `pytest -m "smoke or regression"`

**Q: What do the `-s` and `-v` flags do?**
**A:** 
- `-s`: Disables output capturing. It allows `print()` statements and standard output from the test to be printed directly to the console in real-time.
- `-v`: Stands for verbose mode. It prints the name of every individual test being executed and its status (PASSED/FAILED) instead of just printing dots (`.`).

---

## 9. Pytest Hooks

**Q: What are Pytest hooks? Have you ever used them?**
**A:** Hooks are predefined functions that Pytest calls at different stages of the testing lifecycle (e.g., during initialization, test collection, execution, and reporting). We can override these in `conftest.py` to customize framework behavior.
Examples include:
- `pytest_configure(config)`: Used to register custom markers or initialize global reporting.
- `pytest_runtest_makereport(item, call)`: Used to intercept the test result immediately after execution. We use this heavily to take screenshots on failure or inject custom data (like Test Case IDs) into HTML reports.
- `pytest_html_results_table_header`: A specific hook from `pytest-html` used to add custom columns to the reporting table.

---

## 10. Plugins

**Q: What are some essential Pytest plugins you've used?**
**A:**
- **`pytest-xdist`**: Allows executing tests in parallel across multiple CPU cores to speed up execution time (`pytest -n auto`).
- **`pytest-html`**: Generates a standalone HTML file summarizing the test execution results.
- **`pytest-playwright`**: The official Playwright plugin that automatically provides browser, context, and page fixtures out of the box.
- **`pytest-cov`**: Integrates with the coverage library to measure how much of the application source code was covered by the tests.
- **`pytest-mock`**: Provides the `mocker` fixture for safe, clean object mocking and spy creation.
- **`pytest-rerunfailures`**: Re-runs failed tests to eliminate transient/flaky test failures.

**Q: How do you handle flaky tests in Pytest?**
**A:**
1. **Using `pytest-rerunfailures`**: This plugin automatically re-runs failed tests. You can configure it globally:
   `pytest --reruns 3 --reruns-delay 1` (re-runs failed tests up to 3 times, waiting 1 second between runs).
2. **Targeted marking**: Mark specific tests as flaky using the `@pytest.mark.flaky` decorator:
   ```python
   @pytest.mark.flaky(reruns=5, reruns_delay=2)
   def test_unstable_api():
       assert call_flaky_service() == "success"
   ```
3. **Dynamic / Intelligent Waits**: Avoid static sleeping (`time.sleep()`). Instead, use polling mechanisms or the built-in auto-waiting mechanisms of testing tools (like Playwright's assertions).

---

## 11. Parallel Execution & Concurrency

**Q: How do you run tests in parallel in Pytest?**
**A:** We use the `pytest-xdist` plugin. You can run tests in parallel by specifying the `-n` flag followed by the number of workers (e.g., `pytest -n 4` runs on 4 workers, and `pytest -n auto` automatically detects the number of CPU cores and spawns that many workers).

**Q: How does `pytest-xdist` distribute tests among workers? What are the distribution modes?**
**A:** By default, `pytest-xdist` distributes tests across workers dynamically (i.e., as soon as a worker is free, it gets the next test). This is the `--dist=load` mode. Other modes include:
- `--dist=loadscope`: Groups tests by class or module and sends the groups to the same worker. This is very useful when tests within a module/class share setup or need to run sequentially on the same worker to avoid conflicts.
- `--dist=loadfile`: Groups tests by file, executing tests within the same file on the same worker.
- `--dist=each`: Runs each test on *every* worker (useful for testing cross-platform or multi-environment stability).

**Q: What is a common challenge with parallel execution, and how do you handle shared resources (like databases or APIs)?**
**A:** The biggest challenge is **shared state / race conditions** (e.g., multiple workers trying to read/write the same database record or use the same user account concurrently).
Solutions:
1. **Isolation**: Use unique identifiers (like UUIDs) for any dynamically created data so workers do not collide.
2. **Worker-specific databases**: Spin up individual database containers or schemas per worker, or use worker IDs to namespace database names.
3. **Locking**: Use files or locking mechanisms to ensure only one worker modifies a resource at a time.
4. **`pytest-xdist` shared fixtures**: Since fixtures with `session` scope are executed once *per worker process*, you can use file locks or third-party locking libraries to perform a global initialization (like setting up a database schema) exactly once across all workers.

**Q: How do you run global setup/teardown (like database initialization) only once per test suite run when using `pytest-xdist`?**
**A:** A session-scoped fixture in a parallel run executes on *each* worker process, meaning global setup runs multiple times. To run a setup exactly once, we use a file locking mechanism (e.g., using `FileLock` from `filelock`) to ensure only the first worker performs the setup, while other workers wait and read the result:
```python
import pytest
from filelock import FileLock

@pytest.fixture(scope="session", autouse=True)
def global_setup(tmp_path_factory, worker_id):
    if worker_id == "master":
        # Not running in parallel (single worker)
        perform_global_setup()
        yield
        perform_global_teardown()
        return

    # Get a shared directory across all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent
    fn = root_tmp_dir / "global_setup.lock"
    
    with FileLock(str(fn)):
        # The lock ensures only one worker enters this block at a time
        flag_file = root_tmp_dir / "setup_done.txt"
        if not flag_file.exists():
            perform_global_setup()
            flag_file.write_text("done")
            
    yield
    # Note: Global teardown is more complex because workers terminate independently.
    # Typically, teardown is handled externally or by the master process/CI pipeline.
```

---

## 12. Scenario-Based Questions (Medium to High Difficulty)

**Scenario 1 (Medium): You have a test that creates a database record, asserts the record exists, and then deletes the record. However, if the assertion fails, the test aborts and the delete code is never reached, leaving orphaned data. How do you fix this?**
**A:** I would move the creation and deletion logic into a Pytest fixture using the `yield` keyword. The fixture setup creates the record and yields it to the test. The test performs the assertion. Even if the assertion raises an exception, Pytest guarantees that the code block following the `yield` (the teardown/delete step) will still execute, perfectly cleaning up the orphaned data.

**Example Code:**
```python
import pytest

@pytest.fixture
def db_record():
    # Setup: Create a record
    record = create_record_in_db()
    yield record
    # Teardown: Guaranteed to execute even if the test fails
    delete_record_from_db(record.id)

def test_user_record(db_record):
    # If this assertion fails, db_record's teardown still runs
    assert db_record.status == "active"
```

**Scenario 2 (High): You need to run a suite of tests against 3 different browsers (Chromium, Firefox, WebKit) and 2 different user roles (Admin, Guest). Writing separate test functions for all 6 combinations is highly inefficient. How do you handle this cleanly?**
**A:** I would use Pytest parameterization. I can either stack two `@pytest.mark.parametrize` decorators on the test function (one for browsers, one for roles), or I can parameterize the fixtures themselves using `params=[...]`. Pytest will automatically generate the Cartesian product of all combinations, executing the exact same test logic 6 times automatically without any code duplication.

**Example Code (Stacked Parameterization):**
```python
import pytest

@pytest.mark.parametrize("browser", ["chromium", "firefox", "webkit"])
@pytest.mark.parametrize("role", ["admin", "guest"])
def test_dashboard_access(browser, role):
    # Pytest runs this test 6 times:
    # 1. chromium-admin, 2. chromium-guest, 3. firefox-admin, etc.
    driver = launch_browser(browser)
    login_as(driver, role)
    assert can_access_dashboard(driver, role)
```

**Scenario 3 (High): A test fails randomly 1 out of 10 times, but only when the entire suite is run in parallel using `pytest-xdist`. It never fails when run locally in isolation. What is the likely cause, and how do you fix it?**
**A:** This is a classic "test pollution" or shared state issue. The test is likely modifying a global variable, writing to a shared file, or modifying a static database record that another parallel test is also trying to access or assert against simultaneously. The fix is to ensure the test is perfectly atomic. It should create its own unique test data (e.g., using random UUIDs for usernames) via function-scoped fixtures rather than relying on shared or hardcoded state.

**Example Code (Fixing Shared State):**
```python
import uuid
import pytest

# BAD (Shared State - will conflict when run in parallel):
# def test_create_user():
#     username = "test_user"  # static username conflicts in parallel runs
#     create_user_in_db(username)
#     assert user_exists(username)

# GOOD (Isolated State):
@pytest.fixture
def unique_username():
    # Dynamically generate a unique username for each parallel execution
    return f"user_{uuid.uuid4().hex[:8]}"

def test_create_user_isolated(unique_username):
    create_user_in_db(unique_username)
    assert user_exists(unique_username)
```
