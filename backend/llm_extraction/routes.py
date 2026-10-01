from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, or_
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy import func
from typing import Optional
import uuid


import config
from llm_extraction.model import ExtractionResponse, TextInput
from llm_extraction.schema import ExtractionRecord
import llm_extraction.services as llm_services





router = APIRouter()

@router.get("/info")
async def info(settings: config.Settings = Depends(config.get_settings)):
    return {
        "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
        "DATABASE_URL": settings.DATABASE_URL,
        "FRONTEND_URL": settings.FRONTEND_URL,

    }

@router.post("/api/extract", response_model=ExtractionResponse)
async def extract_knowledge(
    input_data: TextInput, 
    db: Session = Depends(llm_services.get_db)
):
    """Extract knowledge from text using Claude and store in database"""
    
    if not input_data.text.strip():
        raise HTTPException(status_code=400, detail="Text input cannot be empty")
    
    # Get extraction from Claude
    extraction = await llm_services.extract_knowledge_with_claude(input_data.text)
    
    # Save to database
    db_extraction = ExtractionRecord(
        original_text=input_data.text,
        summary=extraction["summary"],
        structured_data=extraction["structured_data"]
    )
    
    db.add(db_extraction)
    db.commit()
    db.refresh(db_extraction)
    
    return ExtractionResponse.from_orm_with_uuid_conversion(db_extraction)

@router.get("/api/extractions")
async def get_extractions(db: Session = Depends(llm_services.get_db)):
    """Get all extractions from database"""
    extractions = db.query(ExtractionRecord).order_by(ExtractionRecord.created_at.desc()).limit(50).all()
    return [
        ExtractionResponse.from_orm_with_uuid_conversion(ext)
        for ext in extractions
    ]

@router.get("/api/extractions/search")
async def search_extractions(
    keyword: Optional[str] = None,
    sentiment: Optional[str] = None,
    category: Optional[str] = None,
    entity: Optional[str] = None,
    topic: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(llm_services.get_db)
):
    """Search and filter extractions based on various criteria"""
    
    print("search_extractions called with filters:", {
        "keyword": keyword,
        "sentiment": sentiment,
        "category": category,
        "entity": entity,
        "topic": topic,
        "date_from": date_from,
        "date_to": date_to,
        "limit": limit
    })
    # Start with base query
    query = db.query(ExtractionRecord)
    
    # Apply filters
    if keyword:
        # Search in original text and summary
        keyword_filter = or_(
            ExtractionRecord.original_text.ilike(f"%{keyword}%"),
            ExtractionRecord.summary.ilike(f"%{keyword}%")
        )
        query = query.filter(keyword_filter)
    
    if sentiment:
        # Filter by sentiment in structured_data
        query = query.filter(
            ExtractionRecord.structured_data.op('->>')('sentiment').ilike(f"%{sentiment}%")
        )
    
    if category:
        # Filter by categories in structured_data
        query = query.filter(
            ExtractionRecord.structured_data.op('->')('categories').astext.ilike(f"%{category}%")
        )
    
    if entity:
        # Filter by entities in structured_data
        query = query.filter(
            ExtractionRecord.structured_data.op('->')('key_entities').astext.ilike(f"%{entity}%")
        )
    
    if topic:
        # Filter by topics in structured_data
        query = query.filter(
            ExtractionRecord.structured_data.op('->')('main_topics').astext.ilike(f"%{topic}%")
        )
    
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            query = query.filter(ExtractionRecord.created_at >= date_from_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            query = query.filter(ExtractionRecord.created_at <= date_to_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    print("about to execute query with filters:")
    # Apply ordering and limit
    extractions = query.order_by(ExtractionRecord.created_at.desc()).limit(min(limit, 100)).all()
    print(extractions)
    return {
        "results": [
            ExtractionResponse.from_orm_with_uuid_conversion(ext)
            for ext in extractions
        ],
        "total_found": len(extractions),
        "filters_applied": {
            "keyword": keyword,
            "sentiment": sentiment,
            "category": category,
            "entity": entity,
            "topic": topic,
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit
        }
    }


@router.get("/api/extractions/{extraction_id}")
async def get_extraction(extraction_id: str, db: Session = Depends(llm_services.get_db)):
    """Get a specific extraction by ID"""
    try:
      
        uui_d_obj = uuid.UUID(str(extraction_id))
      
    except ValueError:
      raise HTTPException(status_code=400, detail="Invalid extraction ID format")
    extraction = db.query(ExtractionRecord).filter(ExtractionRecord.id == uui_d_obj).first()
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    return ExtractionResponse.from_orm_with_uuid_conversion(extraction)


@router.delete("/api/extractions/{extraction_id}")
async def delete_extraction(extraction_id: str, db: Session = Depends(llm_services.get_db)):
    """Delete an extraction"""
    try:
        uui_d_obj = uuid.UUID(str(extraction_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid extraction ID format")
    extraction = db.query(ExtractionRecord).filter(ExtractionRecord.id == uui_d_obj).first()
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    db.delete(extraction)
    db.commit()
    
    return {"message": "Extraction deleted successfully"}


@router.get("/api/filters/sentiments")
def get_sentiments(db: Session = Depends(llm_services.get_db)):
    """
    Return distinct sentiment values from structured_data.
    Sentiment is stored as a scalar (string), not an array.
    """
    sentiments = (
        db.query(ExtractionRecord.structured_data["sentiment"].cast(Text))
        .distinct()
        .all()
    )

    # Flatten results from list of tuples → simple list
    cleaned_sentiments = [s[0].strip('"') for s in sentiments if s[0] is not None]
    return {"sentiments": cleaned_sentiments}
    # return {"sentiments": [s[0] for s in sentiments if s[0] is not None]}



@router.get("/api/filters/categories")
async def get_categories(db: Session = Depends(llm_services.get_db)):
    """Return distinct categories stored in extractions"""
    categories = db.query(
    func.jsonb_array_elements_text(
        ExtractionRecord.structured_data['categories'].cast(JSONB)
    )
).distinct().all()
    flat_categories = [c[0] for c in categories if c[0] is not None]

    return {"categories": flat_categories}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LLM Knowledge Extractor"}
