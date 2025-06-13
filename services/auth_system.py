from typing import Optional, Dict, Any
import asyncio
import logging
import aiohttp
from .token_systems import TokenSystem
from .config_system import ConfigSystem, APIConfig

logger = logging.getLogger(__name__)

class AuthSystem:
    """System for handling authentication and authorization"""
    
    def __init__(self, config_system: ConfigSystem, token_system: TokenSystem):
        self.config = config_system
        self.token_system = token_system
        self.api_config = config_system.get_api_config()
        logger.info("AuthSystem initialized")
    
    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Any:
        """Make an authenticated API request"""
        token = await self.token_system.get_valid_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.api_config.base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers
                ) as response:
                    if response.status == 401:
                        # Token might be invalid, try refreshing
                        await self.token_system._refresh_token()
                        # Retry the request
                        return await self.make_authenticated_request(
                            method, endpoint, data, params
                        )
                    
                    response.raise_for_status()
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Authenticated request failed: {str(e)}")
            raise
    
    async def validate_token(self) -> bool:
        """Validate the current token"""
        try:
            # Make a test request to validate token
            await self.make_authenticated_request("GET", "/auth/validate")
            return True
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return False
    
    async def revoke_token(self):
        """Revoke the current token"""
        try:
            if self.token_system._token_info:
                await self.make_authenticated_request(
                    "POST",
                    "/auth/revoke",
                    data={"token": self.token_system._token_info.access_token}
                )
                self.token_system.clear_tokens()
                logger.info("Token revoked successfully")
        except Exception as e:
            logger.error(f"Token revocation failed: {str(e)}")
            raise
    
    def is_authenticated(self) -> bool:
        """Check if we have a valid token"""
        return self.token_system._token_info is not None
