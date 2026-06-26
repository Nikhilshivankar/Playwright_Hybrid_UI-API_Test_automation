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
    Loads the target API URL from test_data.json configuration.
    """
    import json
    test_data_path = Path(__file__).resolve().parent.parent / "data" / "test_data.json"
    with open(test_data_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    api_url = data["api"]["base_url"]
    
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
