
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any



# Pydantic models
class TextInput(BaseModel):
    text: str

class ExtractionResponse(BaseModel):
    id: str
    original_text: str
    summary: str
    structured_data: Dict[Any, Any]
    created_at: datetime

    class Config:
        from_attributes = True
    
    @classmethod
    def from_orm_with_uuid_conversion(cls, db_obj):
        """Convert SQLAlchemy model to Pydantic with proper UUID handling"""
        return cls(
            id=str(db_obj.id),  # Explicitly convert UUID to string
            original_text=db_obj.original_text,
            summary=db_obj.summary,
            structured_data=db_obj.structured_data,
            created_at=db_obj.created_at
        )

class ExtractionCreate(BaseModel):
    summary: str
    structured_data: Dict[Any, Any]

class SearchFilters(BaseModel):
    keyword: Optional[str] = None
    sentiment: Optional[str] = None
    category: Optional[str] = None
    entity: Optional[str] = None
    topic: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: Optional[int] = 50

