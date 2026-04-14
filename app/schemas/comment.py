from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class CommentCreate(BaseModel):
    body: str

class CommentResponse(BaseModel):
    id: UUID
    case_id: UUID
    author_id: UUID
    body: str
    created_at: datetime

    class Config:
        from_attributes = True
        