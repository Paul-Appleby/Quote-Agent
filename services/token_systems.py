from typing import Optional, Dict
from datetime import datetime, timedelta
import asyncio
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging
from pathlib import Path
import aiohttp

logger = logging.getLogger(__name__)

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"

class TokenSystem:
    """Core system for managing OAuth tokens"""
    
    def __init__(self, config_path: Optional[Path] = None):
        # Load configuration
        if config_path:
            load_dotenv(config_path)
        else:
            load_dotenv()
            
        self._token_info: Optional[TokenInfo] = None
        self._token_lock = asyncio.Lock()
        
        # Load OAuth configuration
        self._load_config()
        
        # Initialize logging
        self._setup_logging()
        
        logger.info("TokenSystem initialized")

    def _load_config(self):
        """Load OAuth configuration from environment"""
        self.client_id = os.getenv("API_CLIENT_ID")
        self.client_secret = os.getenv("API_CLIENT_SECRET")
        self.auth_url = os.getenv("API_AUTH_URL")
        self.token_url = os.getenv("API_TOKEN_URL")
        self.scope = os.getenv("API_SCOPE", "read write")
        
        # Validate required configuration
        if not all([self.client_id, self.client_secret, self.token_url]):
            raise ValueError("Missing required OAuth configuration")

    def _setup_logging(self):
        """Configure logging for the token system"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    async def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary"""
        async with self._token_lock:
            if self._token_info is None or self._is_token_expired():
                await self._refresh_token()
            return self._token_info.access_token

    def _is_token_expired(self) -> bool:
        """Check if token is expired or about to expire"""
        if not self._token_info:
            return True
        return datetime.now() + timedelta(minutes=5) >= self._token_info.expires_at

    async def _refresh_token(self, retry_count: int = 0):
        """Refresh the access token with retry logic"""
        try:
            if self._token_info and self._token_info.refresh_token:
                token_data = await self._refresh_with_refresh_token()
            else:
                token_data = await self._refresh_with_client_credentials()
            
            self._update_token_info(token_data)
            logger.info("Token refreshed successfully")
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            if retry_count < 3:  # Max 3 retries
                logger.info(f"Retrying token refresh (attempt {retry_count + 1})")
                await asyncio.sleep(1)
                await self._refresh_token(retry_count + 1)
            else:
                raise Exception("Max retry attempts reached for token refresh")

    async def _refresh_with_refresh_token(self) -> Dict:
        """Refresh token using refresh token"""
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self._token_info.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        return await self._make_token_request(data)

    async def _refresh_with_client_credentials(self) -> Dict:
        """Get new token using client credentials"""
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope
        }
        return await self._make_token_request(data)

    async def _make_token_request(self, data: dict) -> dict:
        """Make a token request to the OAuth server."""
        async with aiohttp.ClientSession() as session:
            async with session.post(self.token_url, data=data) as response:
                response.raise_for_status()
                return await response.json()

    def _update_token_info(self, token_data: Dict):
        """Update token information"""
        self._token_info = TokenInfo(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", ""),
            expires_at=datetime.now() + timedelta(seconds=token_data["expires_in"]),
            token_type=token_data["token_type"]
        )

    def clear_tokens(self):
        """Clear stored tokens"""
        self._token_info = None
        logger.info("Tokens cleared")
