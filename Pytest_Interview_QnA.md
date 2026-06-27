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

---

## 3. Markers and Test Selection

**Q: What are Pytest Markers?**
**A:** Markers (`@pytest.mark.xyz`) are used to tag tests with specific metadata. You can use them to group tests logically, like `@pytest.mark.smoke`, `@pytest.mark.regression`, or `@pytest.mark.ui`. You can then run specific groups from the command line using the `-m` flag (e.g., `pytest -m smoke`).

**Q: How do you skip a test or mark it as a known failure?**
**A:** 
- **`@pytest.mark.skip(reason="...")`**: Completely skips the test execution.
- **`@pytest.mark.skipif(condition, reason="...")`**: Skips the test dynamically if a condition is met (e.g., `sys.platform == 'win32'`).
- **`@pytest.mark.xfail(reason="Known bug")`**: Runs the test, but expects it to fail. If it fails, it's marked as an "expected failure" (XFAIL) rather than a hard failure. If it unexpectedly passes, it is marked as an XPASS.

---

## 4. Parameterization / Data-Driven Testing

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

## 5. Command Line Execution

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

## 6. Pytest Hooks

**Q: What are Pytest hooks? Have you ever used them?**
**A:** Hooks are predefined functions that Pytest calls at different stages of the testing lifecycle (e.g., during initialization, test collection, execution, and reporting). We can override these in `conftest.py` to customize framework behavior.
Examples include:
- `pytest_configure(config)`: Used to register custom markers or initialize global reporting.
- `pytest_runtest_makereport(item, call)`: Used to intercept the test result immediately after execution. We use this heavily to take screenshots on failure or inject custom data (like Test Case IDs) into HTML reports.
- `pytest_html_results_table_header`: A specific hook from `pytest-html` used to add custom columns to the reporting table.

---

## 7. Plugins

**Q: What are some essential Pytest plugins you've used?**
**A:**
- **`pytest-xdist`**: Allows executing tests in parallel across multiple CPU cores to speed up execution time (`pytest -n auto`).
- **`pytest-html`**: Generates a standalone HTML file summarizing the test execution results.
- **`pytest-playwright`**: The official Playwright plugin that automatically provides browser, context, and page fixtures out of the box.
- **`pytest-cov`**: Integrates with the coverage library to measure how much of the application source code was covered by the tests.
