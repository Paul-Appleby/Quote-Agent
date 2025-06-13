import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from services.token_systems import TokenSystem, TokenInfo

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    return {
        "API_CLIENT_ID": "test_client_id",
        "API_CLIENT_SECRET": "test_client_secret",
        "API_AUTH_URL": "https://test.auth.url",
        "API_TOKEN_URL": "https://test.token.url",
        "API_SCOPE": "test_scope"
    }

@pytest.fixture
def token_system(mock_env_vars):
    """Create a TokenSystem instance with mocked environment"""
    with patch.dict('os.environ', mock_env_vars):
        return TokenSystem()

@pytest.mark.asyncio
async def test_initial_token_generation(token_system):
    """Test initial token generation"""
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        token = await token_system.get_valid_token()
        assert token == "test_access_token"
        assert token_system._token_info is not None
        assert token_system._token_info.access_token == "test_access_token"
        assert token_system._token_info.refresh_token == "test_refresh_token"

@pytest.mark.asyncio
async def test_token_refresh(token_system):
    """Test token refresh when expired"""
    # Set up initial token
    token_system._token_info = TokenInfo(
        access_token="old_token",
        refresh_token="old_refresh_token",
        expires_at=datetime.now() - timedelta(minutes=1),
        token_type="Bearer"
    )

    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        token = await token_system.get_valid_token()
        assert token == "new_access_token"
        assert token_system._token_info.access_token == "new_access_token"

@pytest.mark.asyncio
async def test_token_refresh_retry(token_system):
    """Test token refresh retry logic"""
    # Set up initial token
    token_system._token_info = TokenInfo(
        access_token="old_token",
        refresh_token="old_refresh_token",
        expires_at=datetime.now() - timedelta(minutes=1),
        token_type="Bearer"
    )

    with patch('aiohttp.ClientSession.post') as mock_post:
        # First two attempts fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status = 500
        
        mock_response_success = Mock()
        mock_response_success.status = 200
        mock_response_success.json = AsyncMock(return_value={
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        })
        
        mock_post.side_effect = [
            mock_response_fail.__aenter__.return_value,
            mock_response_fail.__aenter__.return_value,
            mock_response_success.__aenter__.return_value
        ]

        token = await token_system.get_valid_token()
        assert token == "new_access_token"
        assert mock_post.call_count == 3

@pytest.mark.asyncio
async def test_token_expiration_check(token_system):
    """Test token expiration check logic"""
    # Test expired token
    token_system._token_info = TokenInfo(
        access_token="test_token",
        refresh_token="test_refresh_token",
        expires_at=datetime.now() - timedelta(minutes=1),
        token_type="Bearer"
    )
    assert token_system._is_token_expired() is True

    # Test token about to expire (within 5 minutes)
    token_system._token_info = TokenInfo(
        access_token="test_token",
        refresh_token="test_refresh_token",
        expires_at=datetime.now() + timedelta(minutes=4),
        token_type="Bearer"
    )
    assert token_system._is_token_expired() is True

    # Test valid token
    token_system._token_info = TokenInfo(
        access_token="test_token",
        refresh_token="test_refresh_token",
        expires_at=datetime.now() + timedelta(minutes=10),
        token_type="Bearer"
    )
    assert token_system._is_token_expired() is False

def test_clear_tokens(token_system):
    """Test clearing tokens"""
    token_system._token_info = TokenInfo(
        access_token="test_token",
        refresh_token="test_refresh_token",
        expires_at=datetime.now() + timedelta(hours=1),
        token_type="Bearer"
    )
    token_system.clear_tokens()
    assert token_system._token_info is None

@pytest.mark.asyncio
async def test_concurrent_token_requests(token_system):
    """Test concurrent token requests"""
    async def get_token():
        return await token_system.get_valid_token()

    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        # Make multiple concurrent requests
        tasks = [get_token() for _ in range(5)]
        tokens = await asyncio.gather(*tasks)
        
        # Verify all requests got the same token
        assert all(token == "test_access_token" for token in tokens)
        # Verify only one token request was made
        assert mock_post.call_count == 1 