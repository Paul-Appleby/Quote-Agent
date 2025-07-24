#!/usr/bin/env python3
"""
Test script for GHL SMS functionality with OAuth tokens
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ghl_sms_server():
    """Test the GHL SMS server endpoints"""
    
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("TESTING GHL SMS SERVER (OAuth)")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n1. Testing server status...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is running")
            print(f"   Token available: {data.get('token_available', False)}")
            print(f"   Token preview: {data.get('token_preview', 'None')}")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 8000")
        print("   Run: python src/send_ghl_sms.py")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False
    
    # Test 2: Check configuration
    print("\n2. Testing configuration...")
    try:
        response = requests.get(f"{base_url}/test-config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuration test passed")
            print(f"   API URL: {data.get('api_url')}")
            print(f"   Base URL: {data.get('base_url')}")
            print(f"   Token available: {data.get('token_available')}")
            print(f"   Token length: {data.get('token_length')}")
            print(f"   Client ID configured: {data.get('client_id_configured')}")
            print(f"   Client Secret configured: {data.get('client_secret_configured')}")
            
            if not data.get('token_available'):
                print("⚠️  WARNING: No OAuth token available!")
                print("   Check your API_CLIENT_ID and API_CLIENT_SECRET in .env file")
                return False
        else:
            print(f"❌ Configuration test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False
    
    # Test 3: Check token status
    print("\n3. Testing token status...")
    try:
        response = requests.get(f"{base_url}/token-status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('token_available'):
                print(f"✅ Token is valid")
                print(f"   Token type: {data.get('token_type')}")
                print(f"   Expires at: {data.get('expires_at')}")
                print(f"   Token preview: {data.get('token_preview')}")
            else:
                print(f"❌ Token not available: {data.get('error')}")
                return False
        else:
            print(f"❌ Token status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking token status: {e}")
        return False
    
    # Test 4: Send test SMS
    print("\n4. Testing SMS sending...")
    try:
        test_data = {
            "contactId": "8mrENnBig20f0h6gNDvR",
            "message": f"OAuth test message - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        print(f"   Sending to contact: {test_data['contactId']}")
        print(f"   Message: {test_data['message']}")
        
        response = requests.post(f"{base_url}/send-sms-custom", json=test_data, timeout=30)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SMS test completed")
            print(f"   Success: {data.get('success', False)}")
            print(f"   Status code: {data.get('status_code')}")
            print(f"   Token used: {data.get('token_used')}")
            
            if data.get('success'):
                print("🎉 SMS sent successfully!")
            else:
                print("⚠️  SMS request completed but may have failed")
                print(f"   GHL Response: {data.get('response')}")
        else:
            print(f"❌ SMS test failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ SMS test timed out (30 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error testing SMS: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETED")
    print("=" * 60)
    return True

def test_direct_oauth():
    """Test OAuth token generation directly"""
    
    print("\n" + "=" * 60)
    print("TESTING OAUTH TOKEN GENERATION")
    print("=" * 60)
    
    client_id = os.getenv("API_CLIENT_ID")
    client_secret = os.getenv("API_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ API_CLIENT_ID or API_CLIENT_SECRET not found in environment variables")
        return False
    
    print(f"Client ID: {client_id[:10]}...")
    print(f"Client Secret: {client_secret[:10]}...")
    
    try:
        # Import the token handler
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent / "ghl_tokens"))
        from token_handler import get_initial_token, send_sms
        
        print("\nGetting initial token...")
        token = get_initial_token()
        
        if token:
            print("✅ OAuth token generated successfully!")
            print(f"   Token type: {token.get('token_type')}")
            print(f"   Expires in: {token.get('expires_in')} seconds")
            print(f"   Token preview: {token['access_token'][:20]}...")
            
            # Test sending SMS directly
            print("\nTesting direct SMS sending...")
            contact_id = "8mrENnBig20f0h6gNDvR"
            message = f"Direct OAuth test - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            result = send_sms(contact_id, message)
            if result:
                print("✅ Direct SMS sent successfully!")
                return True
            else:
                print("❌ Direct SMS failed")
                return False
        else:
            print("❌ Failed to generate OAuth token")
            return False
            
    except Exception as e:
        print(f"❌ OAuth test error: {e}")
        return False

if __name__ == "__main__":
    print("GHL SMS Testing Tool (OAuth)")
    print("This will test both the server and direct OAuth token generation")
    
    # Test server first
    server_success = test_ghl_sms_server()
    
    # Test direct OAuth
    oauth_success = test_direct_oauth()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Server test: {'✅ PASSED' if server_success else '❌ FAILED'}")
    print(f"OAuth test: {'✅ PASSED' if oauth_success else '❌ FAILED'}")
    
    if not server_success or not oauth_success:
        print("\nTROUBLESHOOTING:")
        print("1. Make sure API_CLIENT_ID and API_CLIENT_SECRET are set in your .env file")
        print("2. Make sure the server is running: python src/send_ghl_sms.py")
        print("3. Check your internet connection")
        print("4. Verify your GHL OAuth credentials are valid")
        print("5. Check if the contact ID exists in your GHL account")
        print("6. Make sure your GHL app has SMS permissions") 