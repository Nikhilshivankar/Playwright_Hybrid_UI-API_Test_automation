from pydantic import BaseModel, Field

class PostCreateRequest(BaseModel):
    """
    Request model for creating a post resource.
    Provides validation and automatically serializes user-friendly Python
    camelcase variables to standard API json tags (e.g. user_id -> userId).
    """
    title: str
    body: str
    user_id: int = Field(serialization_alias="userId", validation_alias="userId")
