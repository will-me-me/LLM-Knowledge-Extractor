from sqlalchemy import create_engine, Column, Text, DateTime, JSON, or_
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from database import Base

# Database Models
class ExtractionRecord(Base):
    __tablename__ = "extractions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    original_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    structured_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

