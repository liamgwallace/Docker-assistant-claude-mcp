"""
Configuration management for Docker Management MCP Server
"""
from pathlib import Path
from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys / Auth
    anthropic_api_key: Optional[str] = None
    claude_auth_mode: Literal["auto", "api", "subscription"] = "auto"
    portainer_token: Optional[str] = None

    # Portainer Configuration
    portainer_url: str = "http://host.docker.internal:9000"
    portainer_endpoint_id: int = 1

    # Docker Configuration
    docker_socket_path: str = "/var/run/docker.sock"
    docker_default_network: str = "web"

    # File System Paths
    stacks_dir: Path = Path("/home/liam/docker/stacks")
    volumes_dir: Path = Path("/home/liam/docker/volumes")
    skills_dir: Path = Path("/app/skills")
    config_dir: Path = Path("/app/config")
    data_dir: Path = Path("/app/data")
    jobs_dir: Path = Path("/app/data/jobs")

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    log_level: str = "INFO"

    # Claude Code Configuration
    claude_code_cli_path: str = "claude"  # Assumes 'claude' is in PATH
    claude_model: str = "claude-sonnet-4-5-20250929"

    # Job Management
    max_job_age_hours: int = 24  # Auto-cleanup old jobs
    job_cleanup_interval_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def model_post_init(self, __context):
        """Ensure directories exist after initialization"""
        # Create data directories if they don't exist
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    @property
    def portainer_auth_header(self) -> dict:
        """Get Portainer authentication header"""
        if not self.portainer_token:
            raise ValueError("PORTAINER_TOKEN is required")
        return {"X-API-Key": self.portainer_token}


# Global settings instance
settings = Settings()
