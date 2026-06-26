import pytest
from utils.logger import logger
from api.definitions.petstore_client import PetstoreClient
from api.models.request_models import OrderCreateRequest
from api.models.response_models import OrderResponse, ApiResponse

@pytest.mark.api
@pytest.mark.regression
def test_place_and_delete_order(petstore_client: PetstoreClient):
    """
    Test Case: Verify placing a store order for a pet and then deleting it.
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
    
    # 2. Get order and verify
    fetched_order: OrderResponse = petstore_client.get_order(order.id)
    assert fetched_order.id == order.id, "Fetched Order ID mismatch"
    
    # 3. Delete order
    delete_res: ApiResponse = petstore_client.delete_order(order.id)
    assert delete_res.code == 200 or str(delete_res.message) == str(order.id), "Failed to delete order"
    
    logger.info("--- API Place & Delete Order Test Completed (PASSED) ---")
