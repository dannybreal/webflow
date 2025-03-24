from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from openai import OpenAI
import os
import logging
import time
import asyncio
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client with proper error handling
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")
client = OpenAI(api_key=api_key) if api_key else None

# Get assistant ID from environment
ASSISTANT_ID = os.environ.get("OPENAI_ASSISTANT_ID")
if not ASSISTANT_ID:
    logger.warning("OPENAI_ASSISTANT_ID not found in environment variables")

logger.info(f"Using OpenAI Assistant ID: {ASSISTANT_ID}")

# FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str
    thread_id: Optional[str] = None

class HistoryRequest(BaseModel):
    thread_id: str
    limit: int = 20

class Message(BaseModel):
    role: str
    content: str
    created_at: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    user_id: str
    thread_id: str
    history: Optional[List[Dict[str, Any]]] = None

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    user_id = data.get("user_id", "default_user")
    thread_id = data.get("thread_id")

    if not message:
        return {"error": "No message provided."}

    # Check if OpenAI client is initialized
    if not client:
        raise HTTPException(status_code=500, detail="OpenAI API key not found or invalid")

    try:
        # If no thread_id is provided, create a new thread
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
        
        # Add the user message to the thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        
        # Run the assistant on the thread
        assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
        if not assistant_id:
            # Fallback to regular chat completion if no assistant ID is configured
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": message}]
            )
            reply = completion.choices[0].message.content
            
            return {
                "reply": reply,
                "user_id": user_id,
                "thread_id": None
            }
        
        # Use the configured assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        # Wait for the run to complete
        while run.status in ["queued", "in_progress"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        
        # Get the assistant's response
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        
        # Find the newest assistant message
        assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
        if assistant_messages:
            reply = assistant_messages[0].content[0].text.value
        else:
            reply = "No response from assistant."
        
        return {
            "reply": reply,
            "user_id": user_id,
            "thread_id": thread_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Chat API is operational"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Check if OpenAI client is initialized
        if not client or not ASSISTANT_ID:
            raise HTTPException(status_code=500, detail="OpenAI API key or Assistant ID not configured")
            
        logger.info(f"Processing message from user {request.user_id}, thread_id: {request.thread_id}")
        
        # Create a new thread if none provided
        thread_id = request.thread_id
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
            logger.info(f"Created new thread {thread_id} for user {request.user_id}")
        
        # Add the user message to the thread
        try:
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=request.message
            )
            logger.info(f"Added message to thread {thread_id}")
        except Exception as e:
            logger.error(f"Error adding message to thread: {str(e)}")
            # If thread doesn't exist, create a new one and try again
            if "thread not found" in str(e).lower():
                logger.info("Thread not found, creating new thread")
                thread = client.beta.threads.create()
                thread_id = thread.id
                client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=request.message
                )
                logger.info(f"Created new thread {thread_id} and added message")
            else:
                raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")
        
        # Run the assistant on the thread
        logger.info(f"Running assistant {ASSISTANT_ID} on thread {thread_id}")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )
        
        # Poll for completion
        max_retries = 30
        retry_count = 0
        
        logger.info(f"Waiting for run {run.id} to complete")
        while retry_count < max_retries:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            
            if run_status.status == "completed":
                logger.info(f"Run {run.id} completed successfully")
                break
            elif run_status.status == "failed":
                error_message = getattr(run_status, 'last_error', {})
                logger.error(f"Run {run.id} failed: {error_message}")
                raise HTTPException(status_code=500, detail=f"Assistant run failed: {error_message}")
            elif run_status.status in ["expired", "cancelled"]:
                logger.error(f"Run {run.id} {run_status.status}")
                raise HTTPException(status_code=500, detail=f"Assistant run {run_status.status}")
            
            # Wait before polling again
            logger.info(f"Run status: {run_status.status}. Waiting before next check.")
            await asyncio.sleep(1)
            retry_count += 1
        
        if retry_count >= max_retries:
            logger.error(f"Timed out waiting for run completion after {max_retries} retries")
            raise HTTPException(status_code=504, detail="Timed out waiting for assistant to respond")
        
        # Get the latest message from the assistant
        logger.info(f"Retrieving latest message from thread {thread_id}")
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        
        if not messages.data:
            logger.error("No messages found in thread after completion")
            raise HTTPException(status_code=500, detail="No response message found from assistant")
        
        assistant_message = messages.data[0]
        response_text = assistant_message.content[0].text.value
        logger.info(f"Retrieved assistant response ({len(response_text)} chars)")
        
        # Get chat history (last 10 messages)
        history = []
        all_messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=10
        )
        
        for msg in reversed(all_messages.data):
            role = "user" if msg.role == "user" else "assistant"
            content = msg.content[0].text.value
            history.append({"role": role, "content": content})
        
        # Return the response
        return ChatResponse(
            response=response_text,
            user_id=request.user_id,
            thread_id=thread_id,
            history=history
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/history")
async def history_endpoint(request: HistoryRequest):
    try:
        # Check if OpenAI client is initialized
        if not client:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
            
        thread_id = request.thread_id
        limit = request.limit
        
        # Validate thread_id
        if not thread_id:
            raise HTTPException(status_code=400, detail="thread_id is required")
            
        logger.info(f"Retrieving history for thread {thread_id}, limit: {limit}")
        
        try:
            # Get messages from the thread
            messages = client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=limit
            )
            
            # Format the messages for the response
            history = []
            for msg in reversed(messages.data):
                role = "user" if msg.role == "user" else "assistant"
                content = msg.content[0].text.value
                created_at = msg.created_at
                
                history.append({
                    "role": role, 
                    "content": content,
                    "created_at": created_at
                })
            
            # Return the response
            return {
                "thread_id": thread_id,
                "messages": history
            }
            
        except Exception as e:
            logger.error(f"Error retrieving thread messages: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unable to retrieve chat history: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error processing history request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 