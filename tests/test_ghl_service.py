import pytest
from unittest.mock import Mock, patch, AsyncMock
from services.ghl_service import GHLService
from services.auth_system import AuthSystem

@pytest.fixture
def mock_auth_system():
    """Create a mock AuthSystem"""
    auth_system = Mock(spec=AuthSystem)
    auth_system.make_authenticated_request = AsyncMock()
    return auth_system

@pytest.fixture
def ghl_service(mock_auth_system):
    """Create a GHLService instance with mocked dependencies"""
    return GHLService(mock_auth_system)

@pytest.mark.asyncio
async def test_get_new_messages(mock_auth_system):
    ghl_service = GHLService(mock_auth_system)
    mock_auth_system.make_authenticated_request.return_value = {
        'messages': [
            {'id': 'msg1', 'body': 'Hello'},
            {'id': 'msg2', 'body': 'World'}
        ]
    }

    messages = await ghl_service.get_new_messages()
    mock_auth_system.make_authenticated_request.assert_called_once()
    call_args = mock_auth_system.make_authenticated_request.call_args.kwargs
    assert call_args['method'] == 'GET'
    assert call_args['endpoint'] == '/conversations/messages'
    assert call_args['params'] == {'status': 'unread'}
    assert call_args['data'] is None
    assert len(messages) == 2
    assert messages[0]['id'] == 'msg1'
    assert messages[1]['id'] == 'msg2'

@pytest.mark.asyncio
async def test_get_new_messages_error(ghl_service, mock_auth_system):
    """Test error handling when getting messages"""
    mock_auth_system.make_authenticated_request.side_effect = Exception("API Error")
    
    messages = await ghl_service.get_new_messages()
    assert messages == []

@pytest.mark.asyncio
async def test_get_contact(mock_auth_system):
    ghl_service = GHLService(mock_auth_system)
    mock_auth_system.make_authenticated_request.return_value = {
        'id': 'contact1',
        'firstName': 'John',
        'lastName': 'Doe'
    }

    contact = await ghl_service.get_contact('contact1')
    mock_auth_system.make_authenticated_request.assert_called_once()
    call_args = mock_auth_system.make_authenticated_request.call_args.kwargs
    assert call_args['method'] == 'GET'
    assert call_args['endpoint'] == '/contacts/contact1'
    assert call_args['data'] is None
    assert call_args['params'] is None
    assert contact['id'] == 'contact1'
    assert contact['firstName'] == 'John'

@pytest.mark.asyncio
async def test_create_contact(mock_auth_system):
    ghl_service = GHLService(mock_auth_system)
    contact_data = {
        'firstName': 'John',
        'lastName': 'Doe',
        'phone': '+1234567890',
        'email': 'john@example.com'
    }
    mock_auth_system.make_authenticated_request.return_value = {
        'id': 'new_contact',
        **contact_data
    }

    contact = await ghl_service.create_contact(
        'John', 'Doe', '+1234567890', 'john@example.com'
    )
    mock_auth_system.make_authenticated_request.assert_called_once()
    call_args = mock_auth_system.make_authenticated_request.call_args.kwargs
    assert call_args['method'] == 'POST'
    assert call_args['endpoint'] == '/contacts'
    assert call_args['data'] == contact_data
    assert contact['id'] == 'new_contact'
    assert contact['firstName'] == 'John'

@pytest.mark.asyncio
async def test_search_contacts(mock_auth_system):
    ghl_service = GHLService(mock_auth_system)
    mock_auth_system.make_authenticated_request.return_value = {
        'contacts': [
            {'id': 'contact1', 'firstName': 'John'},
            {'id': 'contact2', 'firstName': 'Jane'}
        ]
    }

    contacts = await ghl_service.search_contacts('John')
    mock_auth_system.make_authenticated_request.assert_called_once()
    call_args = mock_auth_system.make_authenticated_request.call_args.kwargs
    assert call_args['method'] == 'GET'
    assert call_args['endpoint'] == '/contacts/search'
    assert call_args['params'] == {'query': 'John'}
    assert call_args['data'] is None
    assert len(contacts) == 2
    assert contacts[0]['firstName'] == 'John'

@pytest.mark.asyncio
async def test_send_sms(mock_auth_system):
    ghl_service = GHLService(mock_auth_system)
    mock_auth_system.make_authenticated_request.return_value = {
        'id': 'msg1',
        'status': 'sent'
    }

    result = await ghl_service.send_sms('contact1', 'Hello!', 'loc1')
    mock_auth_system.make_authenticated_request.assert_called_once()
    call_args = mock_auth_system.make_authenticated_request.call_args.kwargs
    assert call_args['method'] == 'POST'
    assert call_args['endpoint'] == '/locations/loc1/conversations/messages'
    assert call_args['data'] == {
        'contactId': 'contact1',
        'body': 'Hello!',
        'channelType': 'sms'
    }
    assert result['status'] == 'sent'

@pytest.mark.asyncio
async def test_send_sms_without_location(mock_auth_system):
    ghl_service = GHLService(mock_auth_system)
    mock_auth_system.make_authenticated_request.return_value = {
        'id': 'msg1',
        'status': 'sent'
    }

    result = await ghl_service.send_sms('contact1', 'Hello!')
    mock_auth_system.make_authenticated_request.assert_called_once()
    call_args = mock_auth_system.make_authenticated_request.call_args.kwargs
    assert call_args['method'] == 'POST'
    assert call_args['endpoint'] == '/conversations/messages'
    assert call_args['data'] == {
        'contactId': 'contact1',
        'body': 'Hello!',
        'channelType': 'sms'
    }
    assert result['status'] == 'sent'

@pytest.mark.asyncio
async def test_error_handling(ghl_service, mock_auth_system):
    """Test error handling in various methods"""
    mock_auth_system.make_authenticated_request.side_effect = Exception("API Error")
    
    # Test get_contact error
    with pytest.raises(Exception) as exc_info:
        await ghl_service.get_contact("contact1")
    assert str(exc_info.value) == "API Error"
    
    # Test create_contact error
    with pytest.raises(Exception) as exc_info:
        await ghl_service.create_contact("John", "Doe", "+1234567890")
    assert str(exc_info.value) == "API Error"
    
    # Test search_contacts error
    with pytest.raises(Exception) as exc_info:
        await ghl_service.search_contacts("John")
    assert str(exc_info.value) == "API Error"
    
    # Test send_sms error
    with pytest.raises(Exception) as exc_info:
        await ghl_service.send_sms("contact1", "Hello!")
    assert str(exc_info.value) == "API Error" 