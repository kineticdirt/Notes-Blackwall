# General-purpose assistant (Pi-style) — runs with Claude or OpenAI-compatible LLM.
# Build from repo root: docker build -f assistant/Dockerfile .
FROM python:3.11-slim

WORKDIR /app

COPY assistant/ ./assistant/
COPY blackwall/__init__.py ./blackwall/
COPY blackwall/prompt_injection/ ./blackwall/prompt_injection/

# Optional: MCP for dynamic tools
RUN pip install --no-cache-dir -r assistant/requirements.txt 2>/dev/null || true

EXPOSE 8765

# Mount API key file at /run/secrets/anthropic_api_key and set PI_LLM_API_KEY_FILE=/run/secrets/anthropic_api_key
ENV PI_HTTP_PORT=8765
CMD ["python3", "-m", "assistant.pi_runner", "--daemon"]
