import pytest
import allure
from pathlib import Path
from playwright.sync_api import Playwright, APIRequestContext
from utils.logger import logger
from config.settings import settings
from pages.login_page import LoginPage
from api.definitions.petstore_client import PetstoreClient
from utils.db_helper import DatabaseHelper

@pytest.fixture(scope="function")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    """
    Function-scoped fixture that provides an APIRequestContext instance
    for performing backend HTTP/API requests.
    """
    logger.info("Initializing api_request_context fixture")
    request_context = playwright.request.new_context()
    yield request_context
    logger.info("Disposing api_request_context fixture")
    request_context.dispose()

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Configures and overrides default browser launch parameters.
    Values are loaded dynamically from settings.py config.
    """
    logger.info(f"Setting browser launch configuration: Headless={settings.HEADLESS}, SlowMo={settings.SLOW_MO}ms")
    return {
        **browser_type_launch_args,
        "headless": settings.HEADLESS,
        "slow_mo": settings.SLOW_MO,
    }

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Configures and overrides default browser context parameters.
    Injects default viewport dimensions and application Base URL.
    """
    logger.info(f"Setting context configuration: Base URL={settings.BASE_URL}")
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "base_url": settings.BASE_URL,
    }

@pytest.fixture
def login_page(page) -> LoginPage:
    """
    Fixture to instantiate and expose the LoginPage object.
    Automatically handles Playwright Page injection.
    """
    logger.info("Initializing LoginPage fixture")
    return LoginPage(page)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest Hook triggered after test steps complete.
    If the test fails, a browser screenshot is captured and attached to the Allure report.
    """
    outcome = yield
    report = outcome.get_result()
    report.markers = [mark.name for mark in item.iter_markers()]
    
    tc_id_marker = item.get_closest_marker("tc_id")
    report.tc_id = tc_id_marker.args[0] if tc_id_marker and tc_id_marker.args else "N/A"

    # Capture screenshots only on failure during test execution phase (call)
    if report.when == "call" and report.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            screenshot_dir = Path("reports/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            screenshot_path = screenshot_dir / f"fail_{item.name}.png"
            
            try:
                page.screenshot(path=str(screenshot_path))
                logger.error(f"Test failure detected. Saved failure screenshot to: {screenshot_path}")
                
                # Attach file to Allure Report
                allure.attach.file(
                    source=str(screenshot_path),
                    name=f"failure_screenshot_{item.name}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception as e:
                logger.error(f"Failed to capture failure screenshot: {e}")

@pytest.fixture
def petstore_client(api_request_context) -> PetstoreClient:
    """
    Fixture to instantiate and expose the PetstoreClient for API tests.
    Loads the target API URL from config settings.
    """
    api_url = settings.API_BASE_URL
    
    logger.info("Initializing PetstoreClient fixture")
    return PetstoreClient(api_request_context, api_url)

@pytest.fixture(scope="session")
def db_helper() -> DatabaseHelper:
    """
    Session-scoped fixture to instantiate and expose the DatabaseHelper.
    Maintains a single connection schema setup for the test duration.
    """
    logger.info("Initializing DatabaseHelper fixture")
    return DatabaseHelper()


def pytest_html_results_table_header(cells):
    # Insert new headers at index 2 (after test name / description)
    cells.insert(2, "<th>TC ID</th>")
    cells.insert(3, "<th>Type</th>")
    cells.insert(4, "<th>Tags</th>")


def pytest_html_results_table_row(report, cells):
    markers = getattr(report, "markers", [])
    # Determine test type: UI vs Non-UI
    if "api" in markers or "performance" in markers:
        test_type = "Non-UI"
    elif "e2e" in markers:
        test_type = "E2E"
    else:
        test_type = "UI"
    
    tags = [m for m in markers if m in ("smoke", "regression", "sanity", "api", "performance", "login", "e2e")]
    tags_str = ", ".join(tags)
    tc_id = getattr(report, "tc_id", "N/A")
    
    cells.insert(2, f"<td>{tc_id}</td>")
    cells.insert(3, f"<td>{test_type}</td>")
    cells.insert(4, f"<td>{tags_str}</td>")


# Dictionary to store final status of each test case
# Keys: nodeid, Values: {"type": "UI"|"Non-UI", "status": "passed"|"failed"|"skipped"}
test_case_results = {}


def pytest_runtest_logreport(report):
    # Determine the test type using the report markers (which are attached in pytest_runtest_makereport)
    markers = getattr(report, "markers", [])
    if "api" in markers or "performance" in markers:
        test_type = "Non-UI"
    else:
        test_type = "UI"

    nodeid = report.nodeid
    
    # Initialize record if not exists
    if nodeid not in test_case_results:
        test_case_results[nodeid] = {
            "type": test_type,
            "status": "passed"
        }
        
    # Update status based on execution phase
    if report.failed:
        test_case_results[nodeid]["status"] = "failed"
    elif report.skipped:
        test_case_results[nodeid]["status"] = "skipped"


def pytest_html_results_summary(prefix, summary, postfix, session):
    ui_passed = sum(1 for res in test_case_results.values() if res["type"] == "UI" and res["status"] == "passed")
    ui_failed = sum(1 for res in test_case_results.values() if res["type"] == "UI" and res["status"] == "failed")
    ui_skipped = sum(1 for res in test_case_results.values() if res["type"] == "UI" and res["status"] == "skipped")
    
    non_ui_passed = sum(1 for res in test_case_results.values() if res["type"] == "Non-UI" and res["status"] == "passed")
    non_ui_failed = sum(1 for res in test_case_results.values() if res["type"] == "Non-UI" and res["status"] == "failed")
    non_ui_skipped = sum(1 for res in test_case_results.values() if res["type"] == "Non-UI" and res["status"] == "skipped")
    
    ui_total = ui_passed + ui_failed + ui_skipped
    non_ui_total = non_ui_passed + non_ui_failed + non_ui_skipped
    
    ui_pass_rate = (ui_passed / ui_total * 100) if ui_total > 0 else 0.0
    non_ui_pass_rate = (non_ui_passed / non_ui_total * 100) if non_ui_total > 0 else 0.0
    
    # Determine colors and badges based on pass rates
    if ui_pass_rate == 100.0:
        ui_badge_bg, ui_badge_color = "#dcfce7", "#166534"
    elif ui_pass_rate >= 80.0:
        ui_badge_bg, ui_badge_color = "#fef9c3", "#854d0e"
    else:
        ui_badge_bg, ui_badge_color = "#fee2e2", "#991b1b"
        
    if non_ui_pass_rate == 100.0:
        non_ui_badge_bg, non_ui_badge_color = "#dcfce7", "#166534"
    elif non_ui_pass_rate >= 80.0:
        non_ui_badge_bg, non_ui_badge_color = "#fef9c3", "#854d0e"
    else:
        non_ui_badge_bg, non_ui_badge_color = "#fee2e2", "#991b1b"
        
    ui_skipped_span = f'<span style="color: #b45309; margin-left: 8px;">| Skipped: <strong>{ui_skipped}</strong></span>' if ui_skipped > 0 else ''
    non_ui_skipped_span = f'<span style="color: #b45309; margin-left: 8px;">| Skipped: <strong>{non_ui_skipped}</strong></span>' if non_ui_skipped > 0 else ''
    
    metrics_html = f"""
    <div class="test-metrics-card" style="
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        font-family: system-ui, -apple-system, sans-serif;
    ">
        <h3 style="
            margin-top: 0;
            margin-bottom: 16px;
            color: #1e293b;
            font-size: 16px;
            font-weight: 600;
            letter-spacing: -0.01em;
        ">Test Performance Metrics (UI vs Non-UI)</h3>
        
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        ">
            <!-- UI Card -->
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 16px;
            ">
                <h4 style="margin: 0 0 12px 0; color: #475569; font-size: 14px; font-weight: 600;">UI Web App Tests</h4>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                    <span style="font-size: 32px; font-weight: 700; color: #1e293b;">{ui_pass_rate:.1f}%</span>
                    <span style="font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 12px; background: {ui_badge_bg}; color: {ui_badge_color};">Pass Rate</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; color: #64748b;">
                    <span>Total: <strong>{ui_total}</strong></span> | 
                    <span style="color: #16a34a;">Passed: <strong>{ui_passed}</strong></span> | 
                    <span style="color: #dc2626;">Failed: <strong>{ui_failed}</strong></span>
                    {ui_skipped_span}
                </div>
            </div>
            
            <!-- Non-UI Card -->
            <div style="
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 16px;
            ">
                <h4 style="margin: 0 0 12px 0; color: #475569; font-size: 14px; font-weight: 600;">Non-UI API/Performance Tests</h4>
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                    <span style="font-size: 32px; font-weight: 700; color: #1e293b;">{non_ui_pass_rate:.1f}%</span>
                    <span style="font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 12px; background: {non_ui_badge_bg}; color: {non_ui_badge_color};">Pass Rate</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; font-size: 12px; color: #64748b;">
                    <span>Total: <strong>{non_ui_total}</strong></span> | 
                    <span style="color: #16a34a;">Passed: <strong>{non_ui_passed}</strong></span> | 
                    <span style="color: #dc2626;">Failed: <strong>{non_ui_failed}</strong></span>
                    {non_ui_skipped_span}
                </div>
            </div>
        </div>
    </div>
    """
    prefix.append(metrics_html)

