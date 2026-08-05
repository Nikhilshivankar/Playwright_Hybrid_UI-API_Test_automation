import pytest
from utils.logger import logger
from api.definitions.petstore_client import PetstoreClient
from api.models.request_models import OrderCreateRequest
from api.models.response_models import OrderResponse, ApiResponse

from utils.db_helper import DatabaseHelper

@pytest.mark.api
@pytest.mark.regression
@pytest.mark.tc_id("TC_009")
def test_place_and_delete_order(petstore_client: PetstoreClient, db_helper: DatabaseHelper):
    """
    Test Case: Verify placing a store order for a pet, validating it in the local database, and then deleting it.
    """
    logger.info("--- API Place & Delete Order Test Started ---")
    
    # 1. Place order
    request_payload = OrderCreateRequest(
        petId=999,
        quantity=2,
        status="placed",
        complete=False
    )
    order: OrderResponse = petstore_client.place_order(request_payload)
    assert order.id is not None, "Order ID is missing"
    assert order.pet_id == request_payload.pet_id, "Pet ID mismatch"
    assert order.quantity == request_payload.quantity, "Quantity mismatch"
    assert order.status == request_payload.status, "Status mismatch"
    
    # 2. Mirror order record in local SQLite database for validation
    db_helper.execute(
        "INSERT INTO orders (id, pet_id, quantity, status, complete) VALUES (?, ?, ?, ?, ?)",
        (order.id, order.pet_id, order.quantity, order.status, order.complete)
    )
    
    # 3. Verify SQLite DB entry matches the API Response details
    db_record = db_helper.fetch_one("SELECT * FROM orders WHERE id = ?", (order.id,))
    assert db_record is not None, "Order record not found in local database"
    assert db_record["id"] == order.id, "Database Order ID mismatch"
    assert db_record["pet_id"] == order.pet_id, "Database Pet ID mismatch"
    assert db_record["quantity"] == order.quantity, "Database quantity mismatch"
    assert db_record["status"] == order.status, "Database status mismatch"
    assert bool(db_record["complete"]) == order.complete, "Database complete flag mismatch"
    
    # 4. Get order and verify via API client
    fetched_order: OrderResponse = petstore_client.get_order(order.id)
    assert fetched_order.id == order.id, "Fetched Order ID mismatch"
    
    # 5. Clean up local DB record
    db_helper.execute("DELETE FROM orders WHERE id = ?", (order.id,))
    
    # 6. Delete order via API client
    delete_res: ApiResponse = petstore_client.delete_order(order.id)
    assert delete_res.code == 200 or str(delete_res.message) == str(order.id), "Failed to delete order"
    
    logger.info("--- API Place & Delete Order Test Completed (PASSED) ---")
