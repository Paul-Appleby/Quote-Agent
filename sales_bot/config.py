from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    GHL_API_KEY: str = os.getenv("GHL_API_KEY", "")
    GHL_API_URL: str = "https://rest.gohighlevel.com/v1"
    FIELDD_API_KEY: str = os.getenv("FIELDD_API_KEY", "")
    FIELDD_API_URL: str = "https://api.fieldd.co/v1"
    
    # Webhook Settings
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///db/sops.db")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # List of pipeline names that should trigger the bot
    ALLOWED_PIPELINE_STAGES: List[str] = [
        "Test (Sales Bot)"
    ]
    
    # Optional list of specific contact IDs to allow (for testing)
    ALLOWED_CONTACT_IDS: Optional[List[str]] = [
        "test_contact_123"  # Replace with your test contact ID
    ]
    
    # Whether to only allow specific contacts (True) or all contacts in allowed pipelines (False)
    RESTRICT_TO_SPECIFIC_CONTACTS: bool = True
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings() 