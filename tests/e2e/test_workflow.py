import json
from pathlib import Path
import pytest
from utils.logger import logger
from pages.login_page import LoginPage
from config.settings import settings

# Resolve and load test data dynamically
TEST_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_data.json"
with open(TEST_DATA_PATH, "r", encoding="utf-8") as file:
    test_data = json.load(file)

@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.tc_id("TC_010")
def test_e2e_user_login_and_logout(login_page: LoginPage):
    """
    Test Case: Complete End-to-End workflow of user logging in and then logging out.
    """
    logger.info("--- Execution Started: E2E User Login and Logout ---")
    
    # 1. Login
    login_page.navigate_to_login()
    login_page.login(settings.TEST_USERNAME, settings.TEST_PASSWORD)
    
    # Assert successful login
    assert login_page.is_success_header_displayed(), "Login success header was not displayed."
    assert login_page.is_logout_button_displayed(), "Logout button was not found."
    
    # 2. Logout (End-to-End flow continuation)
    login_page.click(login_page.LOGOUT_BUTTON, description="Logout Button")
    
    # Assert we are back to login page
    login_page.wait_for_element(login_page.USERNAME_INPUT)
    assert login_page.is_visible(login_page.USERNAME_INPUT), "Did not return to login page after logout."
    assert login_page.is_visible(login_page.PASSWORD_INPUT), "Did not return to login page after logout."
    
    logger.info("--- Execution Completed: E2E User Login and Logout (PASSED) ---")
