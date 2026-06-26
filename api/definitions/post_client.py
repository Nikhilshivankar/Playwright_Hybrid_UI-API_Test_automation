from playwright.sync_api import APIRequestContext
from api.models.request_models import PostCreateRequest
from api.models.response_models import PostResponse
from utils.logger import logger

class PostClient:
    """
    PostClient acts as an API controller/client for `/posts` endpoints.
    It wraps Playwright's APIRequestContext calls, handles status validation,
    and returns strongly-typed response models.
    """
    def __init__(self, request_context: APIRequestContext, base_url: str):
        self.request = request_context
        self.base_url = base_url

    def get_post(self, post_id: int) -> PostResponse:
        """Performs a GET request to retrieve a post by ID."""
        endpoint = f"{self.base_url}/posts/{post_id}"
        logger.info(f"API GET Request -> {endpoint}")
        
        response = self.request.get(endpoint)
        logger.info(f"API GET Response Status: {response.status}")
        assert response.status == 200, f"Expected 200 OK, got {response.status}"
        
        return PostResponse(**response.json())

    def create_post(self, payload: PostCreateRequest) -> PostResponse:
        """Performs a POST request to create a new post resource."""
        endpoint = f"{self.base_url}/posts"
        # Serialize model using alias fields (user_id -> userId)
        payload_data = payload.model_dump(by_alias=True)
        
        logger.info(f"API POST Request -> {endpoint}")
        logger.debug(f"Payload sent: {payload_data}")
        
        response = self.request.post(
            endpoint,
            data=payload_data,
            headers={"Content-type": "application/json; charset=UTF-8"}
        )
        logger.info(f"API POST Response Status: {response.status}")
        assert response.status == 201, f"Expected 201 Created, got {response.status}"
        
        return PostResponse(**response.json())

    def delete_post(self, post_id: int) -> int:
        """Performs a DELETE request to remove a post by ID."""
        endpoint = f"{self.base_url}/posts/{post_id}"
        logger.info(f"API DELETE Request -> {endpoint}")
        
        response = self.request.delete(endpoint)
        logger.info(f"API DELETE Response Status: {response.status}")
        assert response.status == 200, f"Expected 200 OK, got {response.status}"
        
        return response.status
