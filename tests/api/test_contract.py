import json
from pathlib import Path
import pytest
from jsonschema import validate, RefResolver
from api.definitions.petstore_client import PetstoreClient
from api.models.request_models import OrderCreateRequest

# Load OpenAPI/Swagger Specification
SWAGGER_PATH = Path(__file__).resolve().parent.parent.parent / "api" / "specs" / "swagger.json"
with open(SWAGGER_PATH, "r", encoding="utf-8") as f:
    swagger_schema = json.load(f)

def validate_contract(data: dict, schema_ref: str):
    """
    Utility method to validate API JSON response against a specific schema reference
    defined within swagger.json definitions (e.g. '#/definitions/Pet').
    """
    schema = {
        "$ref": schema_ref,
        "definitions": swagger_schema["definitions"]
    }
    # Resolver to handle internal references in swagger.json (like #/definitions/Category)
    resolver = RefResolver.from_schema(swagger_schema)
    validate(instance=data, schema=schema, resolver=resolver)


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.tc_id("TC_010")
def test_pet_contract_schema(petstore_client: PetstoreClient):
    """
    Contract Test: Validates that the GET /pet/findByStatus response conforms 
    strictly to the '#/definitions/Pet' schema in the OpenAPI specification.
    """
    # 1. Fetch available pets
    response = petstore_client.request.get(f"{petstore_client.base_url}/pet/findByStatus", params={"status": "available"})
    assert response.status == 200, "Failed to retrieve available pets"
    
    pets = response.json()
    assert len(pets) > 0, "No pets returned to validate contract"
    
    # 2. Validate the contract of the first item
    validate_contract(pets[0], "#/definitions/Pet")


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.tc_id("TC_011")
def test_order_contract_schema(petstore_client: PetstoreClient):
    """
    Contract Test: Validates that the POST /store/order response conforms
    strictly to the '#/definitions/Order' schema in the OpenAPI specification.
    """
    # 1. Place a mock order
    request_payload = OrderCreateRequest(
        petId=102,
        quantity=1,
        status="placed",
        complete=True
    )
    
    # Call the endpoint directly to get the raw JSON response
    endpoint = f"{petstore_client.base_url}/store/order"
    response = petstore_client.request.post(endpoint, data=request_payload.model_dump(by_alias=True, exclude_none=True))
    assert response.status == 200, "Failed to place mock order for contract testing"
    
    order_json = response.json()
    
    # 2. Validate response contract
    validate_contract(order_json, "#/definitions/Order")
    
    # Teardown: Delete placed order
    petstore_client.delete_order(order_json["id"])
