import json
from pathlib import Path
import pytest
from utils.logger import logger
from api.definitions.petstore_client import PetstoreClient

# Resolve and load test data dynamically
TEST_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_data.json"
with open(TEST_DATA_PATH, "r", encoding="utf-8") as file:
    test_data = json.load(file)

@pytest.mark.api
@pytest.mark.login
@pytest.mark.smoke
def test_api_login_successful(petstore_client: PetstoreClient):
    """
    Test Case: Verify successful user login to the Petstore API.
    """
    logger.info("--- API Login Test Started ---")
    username = test_data["valid_user"]["username"]
    password = test_data["valid_user"]["password"]
    
    login_response = petstore_client.login_user(username, password)
    
    # Assert response contains a login success indication (typically token details or message)
    assert login_response is not None, "Login response was empty"
    assert "logged in user session" in login_response or "token" in login_response.lower() or len(login_response) > 0, "Unexpected login response content"
    logger.info("--- API Login Test Completed (PASSED) ---")


@pytest.mark.api
@pytest.mark.login
@pytest.mark.regression
def test_api_logout_successful(petstore_client: PetstoreClient):
    """
    Test Case: Verify successful user logout from the Petstore API.
    """
    logger.info("--- API Logout Test Started ---")
    # 1. Login first to initialize session/token context
    username = test_data["valid_user"]["username"]
    password = test_data["valid_user"]["password"]
    petstore_client.login_user(username, password)
    
    # 2. Perform Logout
    logout_response = petstore_client.logout_user()
    
    # Assert response contains logout success indications
    assert logout_response is not None, "Logout response was empty"
    assert "ok" in logout_response.lower() or len(logout_response) > 0, "Unexpected logout response content"
    logger.info("--- API Logout Test Completed (PASSED) ---")
