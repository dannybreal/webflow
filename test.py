import requests
import json
import time

def test_health():
    try:
        response = requests.get("http://localhost:8000/api/health")
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error in health check: {e}")
        return False

def test_chat():
    try:
        data = {
            "message": "Hello, this is a test message",
            "user_id": "test_user_123"
        }
        response = requests.post("http://localhost:8000/api/chat", json=data)
        print(f"Chat API status: {response.status_code}")
        response_json = response.json()
        print(f"Response: {json.dumps(response_json, indent=2)}")
        return response.status_code == 200, response_json.get("thread_id")
    except Exception as e:
        print(f"Error in chat test: {e}")
        return False, None

def test_history(thread_id):
    try:
        if not thread_id:
            print("Cannot test history without a valid thread_id")
            return False
            
        data = {
            "thread_id": thread_id
        }
        response = requests.post("http://localhost:8000/api/chat/history", json=data)
        print(f"History API status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error in history test: {e}")
        return False

if __name__ == "__main__":
    print("Testing API endpoints...")
    health_ok = test_health()
    
    # Get a thread ID from the chat API first
    chat_ok, thread_id = test_chat()
    
    # Wait a moment for the message to be processed
    if thread_id:
        print(f"Using thread_id: {thread_id} for history test")
        time.sleep(2)  # Give the API a moment to process
    
    history_ok = test_history(thread_id)
    
    if health_ok and chat_ok and history_ok:
        print("\n✅ All tests passed! The API is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the logs above.") 