from pydantic import BaseModel, Field

class PostResponse(BaseModel):
    """
    Response model representing post items.
    Validates types of properties received back from the API.
    """
    id: int
    title: str
    body: str
    user_id: int = Field(validation_alias="userId", serialization_alias="userId")
