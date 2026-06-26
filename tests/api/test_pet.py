import json
from pathlib import Path
import pytest
from utils.logger import logger
from api.definitions.petstore_client import PetstoreClient
from api.models.request_models import PetCreateRequest
from api.models.response_models import PetResponse
from utils.db_helper import DatabaseHelper

# Resolve and load test data dynamically
TEST_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "test_data.json"
with open(TEST_DATA_PATH, "r", encoding="utf-8") as file:
    test_data = json.load(file)

PET_PAYLOAD_RAW = test_data["api"]["pet_payload"]

@pytest.mark.api
@pytest.mark.smoke
def test_add_and_get_pet(petstore_client: PetstoreClient):
    """
    Test Case: Verify adding a pet and retrieving it by ID.
    """
    logger.info("--- API Add & Get Pet Test Started ---")
    
    # 1. Create request payload
    request_payload = PetCreateRequest(
        name=PET_PAYLOAD_RAW["name"],
        status=PET_PAYLOAD_RAW["status"],
        category=PET_PAYLOAD_RAW["category"],
        photoUrls=PET_PAYLOAD_RAW["photoUrls"],
        tags=PET_PAYLOAD_RAW["tags"]
    )
    
    # 2. Add Pet
    created_pet: PetResponse = petstore_client.add_pet(request_payload)
    assert created_pet.id is not None, "Created pet ID is missing"
    assert created_pet.name == request_payload.name, "Name mismatch"
    assert created_pet.status == request_payload.status, "Status mismatch"
    
    # 3. Get Pet and verify
    fetched_pet: PetResponse = petstore_client.get_pet(created_pet.id)
    assert fetched_pet.id == created_pet.id, "Fetched ID mismatch"
    assert fetched_pet.name == created_pet.name, "Fetched name mismatch"
    assert fetched_pet.status == created_pet.status, "Fetched status mismatch"
    
    # Clean up
    try:
        petstore_client.delete_pet(created_pet.id)
    except Exception as e:
        logger.warning(f"Failed to delete pet during cleanup: {e}")
        
    logger.info("--- API Add & Get Pet Test Completed (PASSED) ---")


@pytest.mark.api
@pytest.mark.regression
def test_update_pet(petstore_client: PetstoreClient):
    """
    Test Case: Verify updating an existing pet's status.
    """
    logger.info("--- API Update Pet Test Started ---")
    
    # 1. Create a pet
    request_payload = PetCreateRequest(
        name="UpdateTestPet",
        status="available",
        photoUrls=["https://example.com/updatetest.jpg"]
    )
    created_pet: PetResponse = petstore_client.add_pet(request_payload)
    
    # 2. Update the pet's status to "sold"
    created_pet.status = "sold"
    updated_pet = petstore_client.update_pet(created_pet)
    assert updated_pet.status == "sold", "Status was not updated to sold"
    
    # 3. Query findByStatus to verify the pet is listed as sold
    sold_pets = petstore_client.find_pets_by_status("sold")
    sold_pet_ids = [pet.id for pet in sold_pets]
    assert created_pet.id in sold_pet_ids, f"Pet {created_pet.id} was not found in sold list"
    
    # Clean up
    try:
        petstore_client.delete_pet(created_pet.id)
    except Exception as e:
        logger.warning(f"Failed to delete pet during cleanup: {e}")
        
    logger.info("--- API Update Pet Test Completed (PASSED) ---")


@pytest.mark.api
@pytest.mark.regression
def test_pet_db_verification(petstore_client: PetstoreClient, db_helper: DatabaseHelper):
    """
    Test Case: Add a pet via API, mirror the record in local SQLite database, 
    and verify the details match the API response.
    """
    logger.info("--- API Pet with DB Verification Test Started ---")
    
    # 1. Add Pet via API
    request_payload = PetCreateRequest(
        name="DBVerificationPet",
        status="pending",
        photoUrls=["https://example.com/dbverify.jpg"],
        category={"id": 2, "name": "Cats"}
    )
    created_pet: PetResponse = petstore_client.add_pet(request_payload)
    
    # 2. Mirror record in local DB (simulating backend sync)
    category_name = created_pet.category.name if created_pet.category else None
    db_helper.execute(
        "INSERT INTO pets (id, name, status, category_name) VALUES (?, ?, ?, ?)",
        (created_pet.id, created_pet.name, created_pet.status, category_name)
    )
    
    # 3. Verify SQLite DB entry matches
    db_record = db_helper.fetch_one("SELECT * FROM pets WHERE id = ?", (created_pet.id,))
    assert db_record is not None, "Pet record not found in local database"
    assert db_record["id"] == created_pet.id, "Database ID mismatch"
    assert db_record["name"] == created_pet.name, "Database name mismatch"
    assert db_record["status"] == created_pet.status, "Database status mismatch"
    assert db_record["category_name"] == category_name, "Database category name mismatch"
    
    # 4. Clean up DB and API resources
    db_helper.execute("DELETE FROM pets WHERE id = ?", (created_pet.id,))
    try:
        petstore_client.delete_pet(created_pet.id)
    except Exception as e:
        logger.warning(f"Failed to delete pet during cleanup: {e}")
        
    logger.info("--- API Pet with DB Verification Test Completed (PASSED) ---")
