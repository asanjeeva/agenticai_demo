"""Configuration management for MyAssistant."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # OpenAI
    openai_api_key: str

    # JIRA
    jira_server: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str

    # GitHub
    github_token: str

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()

        required_vars = [
            "OPENAI_API_KEY",
            "JIRA_SERVER",
            "JIRA_EMAIL",
            "JIRA_API_TOKEN",
            "JIRA_PROJECT_KEY",
            "GITHUB_TOKEN",
        ]

        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Please copy .env.example to .env and fill in your credentials."
            )

        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            jira_server=os.getenv("JIRA_SERVER"),
            jira_email=os.getenv("JIRA_EMAIL"),
            jira_api_token=os.getenv("JIRA_API_TOKEN"),
            jira_project_key=os.getenv("JIRA_PROJECT_KEY"),
            github_token=os.getenv("GITHUB_TOKEN"),
        )


# Global config instance (lazy loaded)
_config: Config | None = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config
