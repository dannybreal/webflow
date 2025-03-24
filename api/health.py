from fastapi import APIRouter, HTTPException
from openai import OpenAI
import os

# Initialize OpenAI client with proper error handling
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

router = APIRouter()

@router.get("/health")
async def health_check():
    try:
        # Check if OpenAI client is initialized
        if not client:
            return {
                "status": "unhealthy",
                "openai_connected": False,
                "error": "OpenAI API key not found"
            }
            
        # Check if we can connect to OpenAI API
        models = client.models.list()
        
        # Check if Assistant ID is configured
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        assistant_configured = assistant_id is not None
        
        return {
            "status": "healthy",
            "openai_connected": True,
            "assistant_configured": assistant_configured
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "openai_connected": False,
            "error": str(e)
        } 