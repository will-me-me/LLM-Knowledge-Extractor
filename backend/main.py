from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from llm_extraction.routes import router as llm_router


# Load environment variables
load_dotenv()


# FastAPI app
app = FastAPI(title="LLM Knowledge Extractor", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(llm_router, tags=["LLM Extraction"])