# CI/CD (Continuous Integration / Continuous Deployment) Interview Q&A

This document serves as a study guide for test automation interviews, focusing specifically on **CI/CD principles** and how they are implemented in this repository using **GitHub Actions**.

---

## 1. CI/CD Basics

**Q: What is Continuous Integration (CI), and why is it important in Test Automation?**
**A:** Continuous Integration is the practice of automatically integrating code changes from multiple contributors into a single software project frequently. In Test Automation, CI ensures that every time a developer commits code or creates a Pull Request, the automated test suite (UI and API) is triggered automatically. This provides immediate feedback on whether the new code broke any existing functionality, catching bugs early before they reach production.

**Q: What CI/CD tool are you using in this framework?**
**A:** We use **GitHub Actions**. It allows us to define custom workflows using YAML files directly within the repository (`.github/workflows/pipeline_runner.yml`). It seamlessly integrates with GitHub events (like pushes and PRs) without needing an external CI server like Jenkins.

---

## 2. GitHub Actions Architecture

**Q: Can you explain the components of your GitHub Actions workflow?**
**A:** A GitHub Actions workflow consists of several key components:
1. **Events (Triggers)**: Defines *when* the pipeline runs (e.g., `on: push` or `on: pull_request`).
2. **Jobs**: A set of steps that execute on the same runner. Our workflow has a single job named `test-execution`.
3. **Runners**: The server environment where the job executes. We use `runs-on: ubuntu-latest`.
4. **Steps**: Individual tasks within a job. Our steps include checking out the code, setting up Python, installing Playwright dependencies, and running Pytest.
5. **Actions**: Pre-built, reusable components (like `actions/checkout@v4` or `actions/setup-python@v5`).

**Q: What is `workflow_dispatch`?**
**A:** `workflow_dispatch` is a specific GitHub Actions trigger that allows us to manually trigger the workflow from the GitHub UI. This is incredibly useful for executing the test suite on-demand without needing to push code.

---

## 3. Environment & Secrets Management

**Q: How do you handle secure credentials (like passwords or API tokens) in the CI pipeline?**
**A:** We never hardcode passwords in the repository. Instead, we use **GitHub Repository Secrets**. 
In our `pipeline_runner.yml`, we securely inject these secrets into the runtime environment:
```yaml
env:
  TEST_USERNAME: ${{ secrets.TEST_USERNAME }}
  TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
```
Our Pytest framework (using `pydantic-settings`) automatically reads these environment variables when the tests execute.

**Q: What is the difference between GitHub Secrets and GitHub Variables?**
**A:** 
- **Secrets**: Encrypted strings used for sensitive data (passwords, API keys). Once saved, you cannot view them again in the UI; they are masked in the workflow logs.
- **Variables**: Non-sensitive configuration data (like `BASE_URL=https://practicetestautomation.com` or `BROWSER=chromium`). They are stored in plain text and are meant to manage environments dynamically without changing the code.

---

## 4. Test Artifacts and Reporting

**Q: If a test fails in the CI pipeline, how do you debug it?**
**A:** When running in a headless CI environment, you cannot physically see the browser. Therefore, artifacts are crucial.
We use the `actions/upload-artifact@v4` action at the very end of our workflow to upload the `reports/` folder (which contains our HTML report, screenshots, and logs). 

**Q: How do you ensure the HTML report is uploaded even if the tests fail?**
**A:** By default, if a step in GitHub Actions fails (like Pytest throwing an exit code 1 due to a failing test), all subsequent steps are skipped. To prevent this and guarantee we get our report, we use the `if: always()` condition on the upload step:
```yaml
- name: Archive Execution Reports & Logs
  if: always()
  uses: actions/upload-artifact@v4
```

---

## 5. Performance and Best Practices

**Q: How do you optimize the execution speed of your CI pipeline?**
**A:** 
1. **Dependency Caching**: In the `actions/setup-python` step, we enable `cache: 'pip'`. This caches the downloaded Python packages across pipeline runs, so we don't have to download `pytest` and `playwright` from scratch every single time.
2. **Parallel Testing**: The `pytest` step is configured to run tests concurrently across multiple threads using `pytest-xdist`.
3. **Headless Mode**: We enforce `HEADLESS: true` via environment variables. Running tests without rendering the physical UI consumes significantly less CPU and memory on the Ubuntu runner.

**Q: How do you handle flaky tests in a CI/CD pipeline?**
**A:** Flaky tests ruin trust in the CI/CD pipeline. To combat them:
1. **Auto-Waiting**: Rely heavily on Playwright's auto-waiting features instead of `time.sleep()`.
2. **Reruns**: We can use the `pytest-rerunfailures` plugin to automatically retry a failed test once or twice before officially failing the pipeline.
3. **Quarantine**: If a test is consistently flaky due to an environment issue, we tag it with `@pytest.mark.skip` or `@pytest.mark.xfail` so it doesn't block developers from merging their code while we investigate the root cause.
