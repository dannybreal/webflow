# FastAPI OpenAI Integration for Vercel

This project provides a FastAPI application that integrates with OpenAI's API, specifically designed for deployment on Vercel.

## Features

- FastAPI backend with API routes
- OpenAI integration with Assistant API support
- Vercel-compatible deployment configuration
- Environment variable configuration

## API Endpoints

- `/api/health` - Health check endpoint
- `/api/chat` - Chat with OpenAI
- `/api/chat/history` - Retrieve chat history

## Deployment

This application is configured for deployment on Vercel. Simply push to the main branch to trigger a deployment

## Project Structure

```
webflow/
├── api/                      # FastAPI endpoints
│   ├── chat.py               # Main chat endpoint using OpenAI Assistant
│   ├── health.py             # Health check endpoint
│   └── __init__.py           # Makes directory a Python package
├── static/                   # Static assets for client-side integration
│   ├── chat-window.html      # Complete HTML chat window
│   └── webflow-integration-guide.md  # Integration instructions
├── .env.sample               # Sample environment variables
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python runtime specification
├── server.py                 # Local development server
└── vercel.json               # Vercel deployment configuration
```

## Setup

1. Clone this repository
2. Create an OpenAI account and get an API key at https://platform.openai.com
3. Create an OpenAI Assistant at https://platform.openai.com/assistants
4. Set up environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_ASSISTANT_ID`: The ID of your OpenAI Assistant

## Deployment

### Deploy to Vercel

The easiest way to deploy this application is using Vercel:

1. Fork or clone this repository
2. Create a Vercel account at https://vercel.com
3. Create a new project in Vercel and link it to your repository
4. Add the environment variables mentioned above
5. Deploy the project

Vercel will automatically detect the Python FastAPI endpoints and deploy them as serverless functions.

### Local Development

To run the project locally:

1. Install Python 3.9 or higher
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.sample` to `.env` and add your API keys
6. Run the server: `python server.py`
7. Open your browser at http://localhost:8000

## Webflow Integration

To integrate the chat in your Webflow site:

1. Deploy this project to Vercel
2. In Webflow, add an "Embed" element to your page
3. Copy the entire content of `static/chat-window.html`
4. Update the `API_URL` in the script section to your Vercel deployment URL
5. Paste the code in the Embed element
6. For members-only areas, place this embed in a pages that requires login

## API Endpoints

### `/api/chat`

- **Method**: POST
- **Purpose**: Send a message to the OpenAI Assistant and get a response
- **Request Body**:
  ```json
  {
    "message": "Your message here",
    "user_id": "unique_user_id",
    "thread_id": "optional_thread_id"
  }
  ```
- **Response**:
  ```json
  {
    "response": "Assistant's response",
    "user_id": "unique_user_id",
    "thread_id": "thread_id_for_conversation",
    "history": [{"role": "user", "content": "message"}, ...]
  }
  ```

### `/api/history`

- **Method**: POST
- **Purpose**: Retrieve chat history for a specific thread
- **Request Body**:
  ```json
  {
    "thread_id": "thread_id_to_retrieve",
    "limit": 20
  }
  ```
- **Response**:
  ```json
  {
    "thread_id": "thread_id",
    "messages": [
      {
        "role": "user",
        "content": "User message",
        "created_at": "timestamp"
      },
      {
        "role": "assistant", 
        "content": "Assistant response",
        "created_at": "timestamp"
      }
    ]
  }
  ```

### `/api/health`

- **Method**: GET
- **Purpose**: Check if the API is operational
- **Response**:
  ```json
  {
    "status": "healthy",
    "message": "API is operational"
  }
  ```

## Performance Considerations

This implementation is optimized for handling concurrent users by:

1. Using FastAPI's async/await capabilities for non-blocking operations
2. Leveraging OpenAI's backend for conversational memory storage
3. Using Vercel's serverless functions for automatic scaling
4. Implementing proper error handling and retries
5. Optimizing the connection between client and server

## License

MIT

## Credits

Built with:
- FastAPI
- OpenAI Assistants API
- Vercel Serverless Functions
- Python 3.9 