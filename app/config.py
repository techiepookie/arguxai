"""Application configuration using Pydantic Settings"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_key: str = "dev_key_change_in_production"
    environment: str = "development"
    
    # Convex Database
    convex_deployment_url: str
    convex_deploy_key: str
    
    # DeepSeek AI
    deepseek_api_key: str
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model_chat: str = "deepseek-chat"
    deepseek_model_vision: str = "deepseek-vl"
    
    # GitHub Integration
    github_token: Optional[str] = None
    github_default_repo: Optional[str] = None
    
    # Figma Integration
    figma_access_token: Optional[str] = Field(default=None, description="Figma personal access token")
    
    # Jira Integration  
    jira_domain: Optional[str] = Field(default=None, description="Jira domain")
    jira_email: Optional[str] = Field(default=None, description="Jira user email")
    jira_api_token: Optional[str] = Field(default=None, description="Jira API token")
    jira_project_key: str = Field(default="CONV", description="Default Jira project key")
    
    # Slack Integration
    slack_webhook_url: Optional[str] = None
    slack_channel: str = "#growth-team"
    slack_leadership_channel: str = "#leadership"
    
    # Anomaly Detection Configuration
    min_drop_percent: float = 12.0
    min_sample_size: int = 100
    sigma_threshold: float = 2.0
    alert_cooldown_minutes: int = 5
    
    # Background Jobs
    monitoring_interval_minutes: int = 2
    measurement_check_hours: int = 1
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Demo Mode
    demo_mode: bool = False
    demo_event_rate: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
