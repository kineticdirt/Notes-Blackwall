# Assistant HTTP API (key-free)

The assistant exposes an HTTP API that **never includes or returns your API key**. You call it with a message and get back a reply in a fixed format.

## Endpoint

**POST** `/message`

- **Request body (JSON):** `{ "message": "your text here" }`
- **Response (JSON):** `{ "reply": "assistant reply text" }`
- **Errors:** `{ "error": "description" }` with HTTP 4xx/5xx as appropriate.

No authentication or API key is sent in the request. The key lives only in the assistant process (or in the key-holder if you use that setup).

## Example

```bash
curl -X POST http://localhost:8765/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

Response:

```json
{ "reply": "Hello! How can I help you today?" }
```

## Iterative use

Call **POST /message** multiple times for multi-turn conversation. Each request is a single user message; the response is the assistant’s reply. The assistant keeps preferences and context in its own state; you do not send or receive keys or tokens in the request/response.

## Response framework

All success responses use the same shape:

| Field   | Type   | Description |
|--------|--------|-------------|
| `reply` | string | The assistant’s reply. Only this field is guaranteed; no key or secret is ever present. |

Error responses:

| Field   | Type   | Description |
|--------|--------|-------------|
| `error` | string | Short error description. |
