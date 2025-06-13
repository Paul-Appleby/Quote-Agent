import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    # Load test environment variables
    test_env_path = Path(__file__).parent / "test.env"
    if test_env_path.exists():
        load_dotenv(test_env_path)
    else:
        # Set default test values if no test.env file exists
        os.environ.update({
            "API_CLIENT_ID": "test_client_id",
            "API_CLIENT_SECRET": "test_client_secret",
            "API_AUTH_URL": "https://test.auth.url",
            "API_TOKEN_URL": "https://test.token.url",
            "API_BASE_URL": "https://test.api.url",
            "API_SCOPE": "test_scope",
            "ENVIRONMENT": "test",
            "LOG_LEVEL": "DEBUG",
            "DEBUG": "true"
        })

@pytest.fixture
def test_data_dir():
    """Get the test data directory"""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def mock_webhook_data():
    """Sample webhook data for testing"""
    return {
        "event": "sms_received",
        "contact": {
            "id": "test_contact",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "+1234567890"
        },
        "message": {
            "id": "test_message",
            "text": "Test message",
            "timestamp": "2024-03-20T12:00:00Z"
        },
        "metadata": {
            "source": "test",
            "campaign": "test_campaign"
        }
    } 