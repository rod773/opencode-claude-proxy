import os
os.environ['ANTHROPIC_API_KEY'] = 'test'

from fastapi.testclient import TestClient
import server.main as sm

# Replace the chat method with a mock implementation

def mock_chat(model, messages, temperature=0.7):
    return "Mocked reply"

sm.claude_agent.chat = mock_chat

client = TestClient(sm.app)

payload = {
    "model": "claude-3-opus-20240229",
    "messages": [
        {"role": "system", "content": "You are an assistant."},
        {"role": "user", "content": "Hello"}
    ]
}

resp = client.post("/v1/chat/completions", json=payload)
print("Status:", resp.status_code)
print("Response JSON:", resp.json())
