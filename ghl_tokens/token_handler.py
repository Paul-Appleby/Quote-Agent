import json, time, requests, os
from dotenv import load_dotenv
import requests
from pathlib import Path
from datetime import datetime, timedelta

load_dotenv()

CLIENT_ID = os.getenv("API_CLIENT_ID")
CLIENT_SECRET = os.getenv("API_CLIENT_SECRET")
REDIRECT_URI = os.getenv("API_REDIRECT_URI")
TOKEN_URL = os.getenv("API_TOKEN_URL", "https://services.leadconnectorhq.com/oauth/token")
BASE_URL = os.getenv("API_BASE_URL", "https://rest.gohighlevel.com/v2")

# Get the directory where token_handler.py is located
TOKEN_DIR = Path(__file__).parent
TOKEN_FILE = TOKEN_DIR / "tokens.json"

def load_tokens():
    """Load tokens from JSON file"""
    try:
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return {}

def save_tokens(tokens):
    """Save tokens to JSON file"""
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=2)
    except Exception as e:
        print(f"Error saving tokens: {e}")

def is_expired(tokens):
    """Check if token is expired"""
    if not tokens or 'expires_at' not in tokens:
        return True
    expires_at = datetime.fromisoformat(tokens['expires_at'])
    return datetime.now() >= expires_at

def get_initial_token():
    """Get initial token using client credentials"""
    try:
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        
        print(f"Requesting token from: {TOKEN_URL}")
        print("Request data:", {k: v[:5] + '...' if k in ['client_id', 'client_secret'] else v for k, v in data.items()})
        
        response = requests.post(TOKEN_URL, data=data)
        if response.status_code != 200:
            print(f"Error response: {response.status_code}")
            print(f"Response body: {response.text}")
        response.raise_for_status()
        
        token_data = response.json()
        
        # Add expiration time
        token_data['expires_at'] = (
            datetime.now() + timedelta(seconds=token_data['expires_in'])
        ).isoformat()
        
        # Save the token
        save_tokens(token_data)
        print("Successfully got and saved initial token")
        return token_data
        
    except Exception as e:
        print(f"Error getting initial token: {e}")
        return None

def get_valid_token():
    """Get a valid token, refreshing if necessary"""
    tokens = load_tokens()
    
    if is_expired(tokens):
        print("Token expired, getting new token...")
        return get_initial_token()
    
    return tokens

def send_sms(contact_id, message):
    """Send SMS using GHL API"""
    token = get_valid_token()
    if not token:
        print("No valid token available")
        return
    
    headers = {
        'Authorization': f"Bearer {token['access_token']}",
        'Content-Type': 'application/json'
    }
    
    data = {
        'contactId': contact_id,
        'message': message,
        'channelType': 'sms'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/messages',
            headers=headers,
            json=data
        )
        response.raise_for_status()
        print("SMS sent successfully!")
        return response.json()
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None

def get_token(key):
    """Get a specific token"""
    tokens = load_tokens()
    return tokens.get(key)

def set_token(key, value):
    """Set a specific token"""
    tokens = load_tokens()
    tokens[key] = value
    save_tokens(tokens)

def clear_tokens():
    """Clear all tokens"""
    save_tokens({})

if __name__ == "__main__":
    # Test the token handler
    print("Testing token handler...")
    
    # Test setting a token
    set_token("test_token", "test_value")
    print("Set test token")
    
    # Test getting a token
    value = get_token("test_token")
    print(f"Got test token: {value}")
    
    # Test clearing tokens
    clear_tokens()
    print("Cleared tokens")
    
    # Verify tokens are cleared
    value = get_token("test_token")
    print(f"Token after clear: {value}")

    # Test getting initial token
    print("Getting initial token...")
    token = get_initial_token()
    if token:
        print("Token received successfully!")
        print(f"Access token: {token['access_token'][:20]}...")
        print(f"Expires at: {token['expires_at']}")
        
        # Test sending SMS
        contact_id = "8mrENnBig20f0h6gNDvR"
        msg = "Hey there! Your WAXD agent is here to help 🚗✨"
        print(f"\nSending test SMS to {contact_id}...")
        send_sms(contact_id, msg)
