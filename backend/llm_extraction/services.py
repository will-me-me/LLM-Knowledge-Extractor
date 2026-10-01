from fastapi import FastAPI, HTTPException, Depends
from anthropic import AsyncAnthropic
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import anthropic
import os
from sqlalchemy import func, case
from typing import Optional, Dict, Any
import json
import uuid
from dotenv import load_dotenv

import config
from database import SessionLocal


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def extract_knowledge_with_claude(text: str) -> Dict[str, Any]:
    """Use Claude to extract summary and structured data from text"""

    api_key = config.get_settings().ANTHROPIC_API_KEY
    if not api_key:
        raise ValueError("Anthropic API key is not set in environment variables.")
    
    prompt = f"""
    Please analyze the following text and provide:
    1. A concise summary (2-3 sentences)
    2. Structured data extraction in JSON format with these fields:
       - key_entities: list of important people, places, organizations mentioned
       - main_topics: list of 3-5 main topics/themes
       - sentiment: overall sentiment (positive, negative, neutral)
       - key_dates: any important dates mentioned
       - action_items: any tasks or actions mentioned
       - categories: suggested categories for this content

    Text to analyze:
    {text}

    Please respond with a JSON object containing 'summary' and 'structured_data' fields.
    """
    
    try:
        client = AsyncAnthropic(api_key=api_key)
        message = await client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            temperature=0.7,
            system=prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
    
        
        response_text = message.content[0].text
        
        # Try to extract JSON from the response
        try:
            # Look for JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                return result
            else:
                # Fallback if JSON extraction fails
                return {
                    "summary": response_text[:200] + "...",
                    "structured_data": {
                        "key_entities": [],
                        "main_topics": ["analysis_failed"],
                        "sentiment": "neutral",
                        "key_dates": [],
                        "action_items": [],
                        "categories": ["unprocessed"]
                    }
                }
        except json.JSONDecodeError:
            # Fallback response
            return {
                "summary": "Failed to parse structured response from Claude",
                "structured_data": {
                    "raw_response": response_text,
                    "processing_error": True
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Claude: {str(e)}")