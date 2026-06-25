import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime
from uuid import uuid4

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from .claude_agent import ClaudeAgent

app = FastAPI(title="OpenAI Chat Completion Proxy for Claude Agent SDK")

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChoiceMessage(BaseModel):
    role: Literal["assistant"]
    content: str

class Choice(BaseModel):
    index: int = 0
    message: ChoiceMessage
    finish_reason: str = "stop"

class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: List[Choice]

# Initialise the Claude Agent wrapper
claude_agent = ClaudeAgent()

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    if request.stream:
        raise HTTPException(status_code=400, detail="Streaming not supported")
    try:
        # Convert Pydantic models to plain dicts for the agent
        content = claude_agent.chat(
            model=request.model,
            messages=[msg.dict() for msg in request.messages],
            temperature=request.temperature,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    now = int(datetime.utcnow().timestamp())
    response = ChatCompletionResponse(
        id=str(uuid4()),
        created=now,
        model=request.model,
        choices=[
            Choice(
                index=0,
                message=ChoiceMessage(role="assistant", content=content),
                finish_reason="stop",
            )
        ],
    )
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server.main:app", host="0.0.0.0", port=port)
