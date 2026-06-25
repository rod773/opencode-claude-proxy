# opencode-claude-proxy

A tiny **OpenAI‑compatible** proxy that forwards chat completion requests to **Claude** using the Anthropic SDK.  OpenCode can be pointed at this service via its `baseURL` configuration (`http://localhost:<PORT>/v1`).

---

## Features

- FastAPI HTTP server
- `POST /v1/chat/completions` endpoint compatible with the OpenAI chat completion schema
- Converts the `messages` payload (system, user, assistant) to the format expected by the Anthropic Claude client
- Returns a response containing `id`, `model`, `created`, and `choices[0].message.content`
- Minimal error handling:
  - `400` for invalid payloads or when `stream: true` is requested (streaming not supported)
  - `500` for internal agent errors
- Configuration via environment variables (`PORT`, `ANTHROPIC_API_KEY`)

---

## Quick start

1. **Clone the repository** (or copy the files into a new directory)
   ```bash
   git clone <repo-url> opencode-claude-proxy
   cd opencode-claude-proxy
   ```

2. **Create an environment file**
   ```bash
   cp .env.example .env
   # Edit .env and set your Anthropic API key
   ```

3. **Install dependencies**
   ```bash
   python -m venv .venv   # optional, but recommended
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Run the server**
   ```bash
   uvicorn server.main:app --host 0.0.0.0 --port $PORT
   ```
   The server will listen on the port defined in `.env` (default 8000).

---

## Using the proxy from OpenCode

Configure OpenCode to use the proxy by setting the base URL to:

```
http://localhost:<PORT>/v1
```

Replace `<PORT>` with the value you set in `.env` (default 8000).  After that, any request that OpenCode sends to the standard OpenAI `/v1/chat/completions` endpoint will be routed to Claude.

---

## Example request

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "claude-3-opus-20240229",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Say hello!"}
        ]
      }'
```

**Response** (formatted JSON)
```json
{
  "id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "object": "chat.completion",
  "created": 1729876543,
  "model": "claude-3-opus-20240229",
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "Hello!"},
      "finish_reason": "stop"
    }
  ]
}
```

---

## Environment variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Port on which the FastAPI server runs. | `8000` |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (required). | `sk-ant-xyz…` |

---

## Limitations & next steps

- **No streaming support** – the proxy rejects requests with `stream: true` (returns 400).
- **Fixed max‑tokens** – currently set to `1024`; adjust in `server/claude_agent.py` if needed.
- **Error reporting** – only generic `500` errors are exposed; extend as required.

Feel free to modify the code to add features such as custom max‑tokens, token usage reporting, or streaming support.
