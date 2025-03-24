from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from openai import OpenAI
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with proper error handling
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=api_key) if api_key else None

router = APIRouter()

class HistoryRequest(BaseModel):
    thread_id: str

@router.post("/chat/history")
async def get_chat_history(request: HistoryRequest):
    try:
        # Check if OpenAI client is initialized
        if not client:
            raise HTTPException(status_code=500, detail="OpenAI API key not found or invalid")
            
        if not request.thread_id:
            return {"error": "No thread_id provided."}
        
        # Get messages from the thread
        messages = client.beta.threads.messages.list(
            thread_id=request.thread_id
        )
        
        # Format and return the messages
        formatted_messages = []
        for msg in messages.data:
            content = ""
            if msg.content and len(msg.content) > 0:
                content = msg.content[0].text.value
            
            formatted_messages.append({
                "id": msg.id,
                "role": msg.role,
                "content": content,
                "created_at": msg.created_at
            })
        
        return {
            "thread_id": request.thread_id,
            "history": formatted_messages
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 