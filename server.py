import os
import logging
from api import app
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded")
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")

# For Vercel serverless deployment
app = app  # This line exposes the app to Vercel

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"Starting server at http://{host}:{port}")
    print(f"OpenAI API Key configured: {'Yes' if os.getenv('OPENAI_API_KEY') else 'No'}")
    print(f"OpenAI Assistant ID configured: {'Yes' if os.getenv('OPENAI_ASSISTANT_ID') else 'No'}")
    
    import uvicorn
    uvicorn.run(app, host=host, port=port) 