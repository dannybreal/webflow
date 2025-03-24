import uvicorn
import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from api import app as api_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded")
    # Log loaded API keys (masked for security)
    openai_key = os.getenv("OPENAI_API_KEY", "")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID", "")
    logger.info(f"OpenAI API Key configured: {'Yes' if openai_key else 'No'}")
    logger.info(f"OpenAI Assistant ID configured: {'Yes' if assistant_id else 'No'}")
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")

# Create main FastAPI app
app = api_app

# Mount static files if the directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Root route
    @app.get("/")
    async def root():
        """Redirect root to the chat window"""
        return RedirectResponse(url="/static/chat-window.html")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting server at http://{host}:{port}")
    print(f"OpenAI API Key configured: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print(f"OpenAI Assistant ID configured: {'Yes' if os.getenv('OPENAI_ASSISTANT_ID') else 'No'}")
    
    uvicorn.run(app, host=host, port=port) 