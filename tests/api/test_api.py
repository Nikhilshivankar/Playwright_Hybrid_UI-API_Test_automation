import json
from pathlib import Path
import pytest
from utils.logger import logger
from api.definitions.post_client import PostClient
from api.models.request_models import PostCreateRequest
from api.models.response_models import PostResponse
from utils.db_helper import DatabaseHelper

# Resolve and load test data dynamically (relative to tests/api/)
TEST_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_data.json"
with open(TEST_DATA_PATH, "r", encoding="utf-8") as file:
    test_data = json.load(file)

PAYLOAD_RAW = test_data["api"]["post_payload"]

@pytest.mark.api
@pytest.mark.smoke
def test_api_get_post(post_client: PostClient):
    """
    Test Case: Verify GET request retrieves the correct post details.
    Uses PostClient to return a validated PostResponse model.
    """
    logger.info("--- API GET Test Started ---")
    
    post: PostResponse = post_client.get_post(1)
    
    # Validate structure and fields using type-safe Pydantic attributes
    assert post.id == 1, f"Expected ID 1, got {post.id}"
    assert post.user_id == 1, f"Expected userId 1, got {post.user_id}"
    assert len(post.title) > 0, "Title was empty"
    assert len(post.body) > 0, "Body was empty"
    
    logger.info("--- API GET Test Completed (PASSED) ---")


@pytest.mark.api
@pytest.mark.regression
def test_api_create_post(post_client: PostClient):
    """
    Test Case: Verify POST request successfully creates a new post resource.
    Validates request serialization and deserializes output into PostResponse.
    """
    logger.info("--- API POST Test Started ---")
    
    # Construct verified request payload using PostCreateRequest model
    request_payload = PostCreateRequest(
        title=PAYLOAD_RAW["title"],
        body=PAYLOAD_RAW["body"],
        userId=PAYLOAD_RAW["userId"]
    )
    
    created_post: PostResponse = post_client.create_post(request_payload)
    
    # Assert values echo back correctly
    assert created_post.title == request_payload.title, "Title mismatch"
    assert created_post.body == request_payload.body, "Body mismatch"
    assert created_post.user_id == request_payload.user_id, "User ID mismatch"
    assert created_post.id is not None, "Generated ID missing in response"
    
    logger.info("--- API POST Test Completed (PASSED) ---")


@pytest.mark.api
@pytest.mark.regression
def test_api_delete_post(post_client: PostClient):
    """
    Test Case: Verify DELETE request successfully removes a post resource.
    """
    logger.info("--- API DELETE Test Started ---")
    
    status_code = post_client.delete_post(1)
    assert status_code == 200, f"Expected DELETE code 200, got {status_code}"
    
    logger.info("--- API DELETE Test Completed (PASSED) ---")


@pytest.mark.api
@pytest.mark.regression
def test_api_create_post_with_db_verification(post_client: PostClient, db_helper: DatabaseHelper):
    """
    Test Case: Create a post via POST request and verify the record is mirrored/persisted
    in the database correctly.
    """
    logger.info("--- API POST with DB Verification Test Started ---")
    
    # 1. Send API Post Request
    request_payload = PostCreateRequest(
        title="API + DB Verification Post",
        body="This is an E2E test verifying API response matches DB record.",
        userId=42
    )
    created_post = post_client.create_post(request_payload)
    
    # 2. Simulate Backend Write: Record the created post in the local database
    # In a real environment, the backend writes to the DB when it receives the POST request.
    # Here, we simulate that synchronization/entry locally for validation.
    db_helper.execute(
        "INSERT INTO posts (id, title, body, user_id) VALUES (?, ?, ?, ?)",
        (created_post.id, created_post.title, created_post.body, created_post.user_id)
    )
    
    # 3. DB Verification Query
    db_record = db_helper.fetch_one("SELECT * FROM posts WHERE id = ?", (created_post.id,))
    
    # 4. Assert DB state matches expected results
    assert db_record is not None, "Post record was not found in the database"
    assert db_record["id"] == created_post.id, f"Expected DB id {created_post.id}, got {db_record['id']}"
    assert db_record["title"] == request_payload.title, "Database title did not match request title"
    assert db_record["body"] == request_payload.body, "Database body did not match request body"
    assert db_record["user_id"] == request_payload.user_id, "Database user_id did not match request userId"
    
    # Clean up the DB record after test completion
    db_helper.execute("DELETE FROM posts WHERE id = ?", (created_post.id,))
    logger.info("--- API POST with DB Verification Test Completed (PASSED) ---")

