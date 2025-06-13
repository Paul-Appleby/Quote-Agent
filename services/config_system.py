from pathlib import Path
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class APIConfig(BaseModel):
    base_url: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    scope: str = "read write"

class ConfigSystem:
    """System for managing configuration"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(".env")
        self._load_config()
        self._setup_logging()
    
    def _load_config(self):
        """Load configuration from environment"""
        load_dotenv(self.config_path)
        
        # Load API configuration
        self.api_config = APIConfig(
            base_url=os.getenv("API_BASE_URL", ""),
            client_id=os.getenv("API_CLIENT_ID", ""),
            client_secret=os.getenv("API_CLIENT_SECRET", ""),
            auth_url=os.getenv("API_AUTH_URL", ""),
            token_url=os.getenv("API_TOKEN_URL", ""),
            scope=os.getenv("API_SCOPE", "read write")
        )
        
        # Load other configuration
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        self._validate_config()
    
    def _setup_logging(self):
        """Configure logging"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, self.log_level))
    
    def _validate_config(self):
        """Validate required configuration"""
        required_vars = [
            "base_url",
            "client_id",
            "client_secret",
            "token_url"
        ]
        
        missing = [
            var for var in required_vars 
            if not getattr(self.api_config, var)
        ]
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}"
            )
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration"""
        return self.api_config
    
    def get_environment(self) -> str:
        """Get current environment"""
        return self.environment
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.debug
    
    def get_log_level(self) -> str:
        """Get current log level"""
        return self.log_level
