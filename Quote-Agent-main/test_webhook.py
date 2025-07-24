import requests
import json
import time

def test_webhook_server():
    """Test the webhook server locally"""
    
    # Test data that mimics GHL webhook
    test_data = {
        "customData": {
            "Quote_First_Name": "John",
            "Quote_Last_Name": "Doe", 
            "Quote_Email": "john.doe@example.com",
            "Quote_Phone": "555-123-4567",
            "Quote_Address": "123 Main St, Test City, CA 90210",
            "Quote_Package": "Basic Wash",
            "Quote_Car_Size": "Sedan"
        }
    }
    
    base_url = "http://localhost:5000"
    
    print("=== Testing Webhook Server ===")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Test 2: Send webhook data
    print("\n2. Testing webhook endpoint...")
    try:
        response = requests.post(f"{base_url}/webhook", json=test_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Test 3: Retrieve webhook data
    print("\n3. Testing data retrieval...")
    try:
        response = requests.get(f"{base_url}/latest_webhook")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('data_received'):
            print("✅ Webhook data successfully stored and retrieved!")
        else:
            print("❌ No webhook data found")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    # Test 4: Clear webhook data
    print("\n4. Testing data clearing...")
    try:
        response = requests.post(f"{base_url}/webhook", json={"clear": True})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Verify data is cleared
        response = requests.get(f"{base_url}/latest_webhook")
        data = response.json()
        if not data.get('data_received'):
            print("✅ Webhook data successfully cleared!")
        else:
            print("❌ Webhook data not cleared")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    print("\n=== All Tests Passed! ===")
    return True

if __name__ == "__main__":
    print("Make sure the webhook server is running first:")
    print("python quote_bot/server.py")
    print("\nThen run this test script in another terminal.")
    
    input("\nPress Enter to start testing...")
    
    if test_webhook_server():
        print("\n🎉 Webhook server is working correctly!")
        print("Ready to deploy to Railway!")
    else:
        print("\n❌ Webhook server has issues. Check the server logs.") 