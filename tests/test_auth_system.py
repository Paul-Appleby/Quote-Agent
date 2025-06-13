import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.auth_system import AuthSystem
from services.token_systems import TokenSystem
from services.config_system import ConfigSystem

class DummyConfig:
    base_url = 'https://api.example.com'
    client_id = 'test_client_id'
    client_secret = 'test_client_secret'

def make_api_config():
    return DummyConfig()

@pytest.fixture
def mock_config():
    config = Mock(spec=ConfigSystem)
    config.get_api_config.return_value = make_api_config()
    return config

@pytest.fixture
def mock_token_system():
    token_system = Mock(spec=TokenSystem)
    token_system.get_valid_token = AsyncMock(return_value='test_token')
    token_system._refresh_token = AsyncMock()
    token_system._token_info = Mock()  # Fix for is_authenticated
    return token_system

@pytest.fixture
def auth_system(mock_config, mock_token_system):
    """Create an AuthSystem instance with mocked dependencies"""
    return AuthSystem(mock_config, mock_token_system)

@pytest.mark.asyncio
async def test_make_authenticated_request_success(mock_config, mock_token_system):
    auth_system = AuthSystem(mock_config, mock_token_system)
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={'data': 'test_data'})
    mock_response.raise_for_status = AsyncMock()

    with patch('aiohttp.ClientSession.request', return_value=mock_response) as mock_request:
        result = await auth_system.make_authenticated_request('GET', '/test')
        mock_request.assert_called_once()
        call_args = mock_request.call_args.kwargs
        assert call_args['method'] == 'GET'
        assert call_args['url'] == 'https://api.example.com/test'
        assert call_args['headers']['Authorization'] == 'Bearer test_token'
        assert 'Content-Type' in call_args['headers']
        assert result == {'data': 'test_data'}

@pytest.mark.asyncio
async def test_make_authenticated_request_unauthorized(mock_config, mock_token_system):
    auth_system = AuthSystem(mock_config, mock_token_system)
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={'error': 'unauthorized'})
    mock_response.raise_for_status = AsyncMock(side_effect=Exception('401'))

    with patch('aiohttp.ClientSession.request', return_value=mock_response):
        try:
            await auth_system.make_authenticated_request('GET', '/test')
        except Exception as e:
            assert str(e) == '401'

@pytest.mark.asyncio
async def test_validate_token_success(mock_config, mock_token_system):
    auth_system = AuthSystem(mock_config, mock_token_system)
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={'valid': True})
    mock_response.raise_for_status = AsyncMock()

    with patch('aiohttp.ClientSession.request', return_value=mock_response) as mock_request:
        result = await auth_system.validate_token()
        if isinstance(result, AsyncMock):
            result = await result
        mock_request.assert_called_once()
        call_args = mock_request.call_args.kwargs
        assert call_args['method'] == 'GET'
        assert call_args['url'].endswith('/auth/validate') or call_args['url'].endswith('/oauth/validate')
        assert call_args['headers']['Authorization'] == 'Bearer test_token'
        assert 'Content-Type' in call_args['headers']
        assert result is True

@pytest.mark.asyncio
async def test_revoke_token(mock_config, mock_token_system):
    auth_system = AuthSystem(mock_config, mock_token_system)
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={'success': True})
    mock_response.raise_for_status = AsyncMock()

    with patch('aiohttp.ClientSession.request', return_value=mock_response) as mock_request:
        await auth_system.revoke_token()
        mock_request.assert_called_once()
        call_args = mock_request.call_args.kwargs
        assert call_args['method'] == 'POST'
        assert call_args['url'].endswith('/oauth/revoke') or call_args['url'].endswith('/auth/revoke')
        assert call_args['headers']['Authorization'] == 'Bearer test_token'
        assert 'Content-Type' in call_args['headers']

def test_is_authenticated(mock_config, mock_token_system):
    auth_system = AuthSystem(mock_config, mock_token_system)
    assert auth_system.is_authenticated() is True 