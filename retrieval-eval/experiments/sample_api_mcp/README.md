# Sample API + MCP (real-world style)

REST API with **list**, **get by id**, and **search** (real-world patterns). Same server exposes **MCP** at `POST /mcp` so you can compare traditional MCP (Claude selects tool) vs text-only micro (nano commits to tool).

## Endpoints

| REST | MCP tool | Description |
|------|----------|-------------|
| GET /api/posts | listPosts | List posts (limit, offset) |
| GET /api/posts/:id | getPost | Get post by id |
| GET /api/posts/search?q= | searchPosts | Search by title/body |
| GET /api/users | listUsers | List users |
| GET /api/users/:id | getUser | Get user by id |

## Run server

```bash
cd retrieval-eval
pip install -r experiments/requirements-sample.txt
uvicorn experiments.sample_api_mcp.api:app --host 127.0.0.1 --port 8765
```

Then run MvM comparison (see retrieval-eval/experiments/README-MVM.md or mvm_sample_api_runner.py).

## MCP URL

Default: `http://localhost:8765/mcp`. Override with `SAMPLE_MCP_URL`.
