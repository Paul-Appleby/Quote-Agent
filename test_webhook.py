#!/usr/bin/env python3
"""
Test script to simulate GoHighLevel webhook payload
"""

import requests
import json

# The actual webhook payload we received earlier
test_payload = {
    "customerId": "8mrENnBig20f0h6gNDvR",
    "message": {
        "content": "Hi, I need car detailing for my Honda Civic",
        "timestamp": "2024-01-15T10:30:00Z"
    },
    "customer": {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com"
    },
    "pipeline_stage": "New Lead",
    "locationId": "test_location_123",
    "userId": "test_user_456"
}

def test_webhook():
    """Test the webhook endpoint with our sample payload"""
    
    webhook_url = "http://localhost:5000/webhook"
    
    print("Testing webhook endpoint...")
    print(f"URL: {webhook_url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Send POST request to webhook
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Webhook test successful!")
            result = response.json()
            print(f"AI Response: {result.get('ai_response', 'No response')}")
            print(f"Pipeline Stage: {result.get('pipeline_stage', 'Unknown')}")
            print(f"Conversation ID: {result.get('conversation_id', 'Unknown')}")
        else:
            print("\n❌ Webhook test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed! Make sure the webhook server is running.")
        print("Start it with: python src/webhook_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_server_status():
    """Test if the webhook server is running"""
    
    test_url = "http://localhost:5000/webhook/test"
    
    try:
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            print("✅ Webhook server is running!")
            return True
        else:
            print("❌ Webhook server returned error status")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Webhook server is not running")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("=== GoHighLevel Webhook Test ===")
    
    # First check if server is running
    if test_server_status():
        # Then test the webhook
        test_webhook()
    else:
        print("\nTo start the webhook server, run:")
        print("python src/webhook_server.py") 