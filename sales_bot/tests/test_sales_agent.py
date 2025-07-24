import pytest
from sales_agent import handle_webhook, verify_webhook_signature, generate_response

@pytest.mark.asyncio
async def test_handle_webhook_success():
    """Test successful webhook handling"""
    test_data = {
        "message": "Hello",
        "contact": {
            "id": "123",
            "name": "Test User",
            "phone": "+1234567890",
            "email": "test@example.com"
        }
    }
    
    result = await handle_webhook(test_data)
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_handle_webhook_invalid_signature():
    """Test webhook handling with invalid signature"""
    test_data = {
        "message": "Hello",
        "contact": {
            "id": "123",
            "name": "Test User"
        }
    }
    
    # Mock verify_webhook_signature to return False
    def mock_verify(data):
        return False
    
    # Replace the real function with our mock
    import sales_agent
    sales_agent.verify_webhook_signature = mock_verify
    
    result = await handle_webhook(test_data)
    assert result["status"] == "error"

def test_generate_response():
    """Test response generation"""
    message = "Hello"
    sop_data = {
        "templates": {
            "greeting": "Hi there! How can I help you today?"
        }
    }
    
    response = generate_response(message, sop_data)
    assert isinstance(response, str)
    assert len(response) > 0 