import json
from pathlib import Path
import pytest
from utils.logger import logger
from pages.login_page import LoginPage
from config.settings import settings

# Resolve and load test data dynamically (relative to tests/ui/)
TEST_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_data.json"
with open(TEST_DATA_PATH, "r", encoding="utf-8") as file:
    test_data = json.load(file)

@pytest.mark.login
@pytest.mark.smoke
@pytest.mark.tc_id("TC_001")
def test_login_successful(login_page: LoginPage):
    """
    Test Case: Verify successful login with correct username and password.
    Verifies header changes to 'Logged In Successfully' and log out option appears.
    """
    logger.info("--- Execution Started: test_login_successful ---")
    login_page.navigate_to_login()
    
    login_page.login(settings.TEST_USERNAME, settings.TEST_PASSWORD)
    
    # Assert successful login header is displayed
    assert login_page.is_success_header_displayed(), "Login success header was not displayed."
    
    # Assert message text matches expected
    header_text = login_page.get_success_message_text()
    expected_message = test_data["validation_messages"]["success_login_message"]
    assert expected_message in header_text, f"Expected '{expected_message}' inside '{header_text}' but not found."
    
    # Assert logout button is displayed
    assert login_page.is_logout_button_displayed(), "Logout button was not found on the page."
    logger.info("--- Execution Completed: test_login_successful (PASSED) ---")


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.tc_id("TC_002")
def test_login_invalid_username(login_page: LoginPage):
    """
    Test Case: Verify validation message displayed with invalid username and valid password.
    """
    logger.info("--- Execution Started: test_login_invalid_username ---")
    login_page.navigate_to_login()
    
    invalid_username = test_data["invalid_user"]["username"]
    valid_password = settings.TEST_PASSWORD
    login_page.login(invalid_username, valid_password)
    
    # Assert expected error message matches
    error_message = login_page.get_error_message()
    expected_error = test_data["validation_messages"]["invalid_username_error"]
    assert expected_error in error_message, f"Expected '{expected_error}' inside '{error_message}' but not found."
    logger.info("--- Execution Completed: test_login_invalid_username (PASSED) ---")


@pytest.mark.login
@pytest.mark.regression
@pytest.mark.tc_id("TC_003")
def test_login_invalid_password(login_page: LoginPage):
    """
    Test Case: Verify validation message displayed with valid username and invalid password.
    """
    logger.info("--- Execution Started: test_login_invalid_password ---")
    login_page.navigate_to_login()
    
    valid_username = settings.TEST_USERNAME
    invalid_password = test_data["invalid_user"]["password"]
    login_page.login(valid_username, invalid_password)
    
    # Assert expected error message matches
    error_message = login_page.get_error_message()
    expected_error = test_data["validation_messages"]["invalid_password_error"]
    assert expected_error in error_message, f"Expected '{expected_error}' inside '{error_message}' but not found."
    logger.info("--- Execution Completed: test_login_invalid_password (PASSED) ---")
