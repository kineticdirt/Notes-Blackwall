from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gateway_port: int = 9000
    gateway_host: str = "0.0.0.0"
    jwt_secret: str = "change-me-in-production"
    rate_limit_rpm: int = 60
    log_level: str = "info"

    blackwall_url: str = "http://localhost:8000"
    workflow_canvas_url: str = "http://localhost:8080"
    agent_system_url: str = "http://localhost:8010"
    nightshade_url: str = "http://localhost:8020"

    class Config:
        env_file = ".env"


ROUTES = {
    "/api/blackwall": "blackwall_url",
    "/api/workflow": "workflow_canvas_url",
    "/api/agents": "agent_system_url",
    "/api/nightshade": "nightshade_url",
}
