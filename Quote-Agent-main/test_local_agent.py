import requests
import json
import sys

def test_local_agent_connection():
    """Test if local agent can connect to webhook server"""
    
    print("=== Testing Local Agent Connection ===")
    
    # Test the webhook URL that local_agent.py uses
    webhook_url = "https://ghlwebhook-production.up.railway.app/latest_webhook"
    
    print(f"Testing connection to: {webhook_url}")
    
    try:
        response = requests.get(webhook_url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ Local agent can connect to webhook server!")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server might not be running")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_clear():
    """Test the clear webhook functionality"""
    
    print("\n=== Testing Webhook Clear Function ===")
    
    webhook_url = "https://ghlwebhook-production.up.railway.app/webhook"
    
    try:
        response = requests.post(webhook_url, json={"clear": True}, timeout=10)
        print(f"Clear Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Clear Response: {json.dumps(data, indent=2)}")
            print("✅ Webhook clear functionality works!")
            return True
        else:
            print(f"❌ Clear failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Clear error: {e}")
        return False

if __name__ == "__main__":
    print("Testing local agent connection to Railway webhook server...")
    
    # Test connection
    if test_local_agent_connection():
        # Test clear functionality
        test_webhook_clear()
        
        print("\n🎉 Local agent is ready to connect to Railway!")
        print("You can now run: python quote_bot/local_agent.py")
    else:
        print("\n❌ Local agent cannot connect to Railway webhook server")
        print("Make sure the Railway deployment is live and accessible") 