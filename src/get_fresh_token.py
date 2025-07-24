#!/usr/bin/env python3
"""
Get Fresh GoHighLevel OAuth Token
This script helps you get a fresh authorization code and exchange it for a token
"""

import requests
import json
import webbrowser
from urllib.parse import urlencode

# Your app credentials
CLIENT_ID = "6835011c08f18f1088f92f9f-mcnl7omh"
CLIENT_SECRET = "26841d60-60b4-42ba-8303-94ef7ab8b6ec"
REDIRECT_URI = "https://github.com"

def get_authorization_url():
    """Generate the authorization URL"""
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'sms.readonly sms.send',
        'state': 'random_state_string'
    }
    
    auth_url = f"https://marketplace.gohighlevel.com/oauth/chooselocation?{urlencode(params)}"
    return auth_url

def exchange_code_for_token(authorization_code):
    """Exchange authorization code for access token"""
    url = "https://services.leadconnectorhq.com/oauth/token"
    
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print("Sending OAuth token request...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, data=payload, headers=headers)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Token received:")
        token_data = response.json()
        print(json.dumps(token_data, indent=2))
        
        # Save token to file
        with open('ghl_tokens/tokens.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        print("\n💾 Token saved to ghl_tokens/tokens.json")
        
        return token_data
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        error_data = response.json()
        print(json.dumps(error_data, indent=2))
        return None

def main():
    print("=" * 60)
    print("GoHighLevel OAuth Token Generator")
    print("=" * 60)
    
    print("\nStep 1: Get Authorization Code")
    print("-" * 40)
    
    auth_url = get_authorization_url()
    print(f"Authorization URL: {auth_url}")
    
    print("\nOpening browser for authorization...")
    try:
        webbrowser.open(auth_url)
    except:
        print("Could not open browser automatically.")
    
    print("\n📋 Instructions:")
    print("1. Complete the authorization in your browser")
    print("2. You'll be redirected to a URL like:")
    print(f"   {REDIRECT_URI}?code=AUTHORIZATION_CODE&state=random_state_string")
    print("3. Copy the 'code' parameter from the URL")
    
    print("\nStep 2: Exchange Code for Token")
    print("-" * 40)
    
    # Get authorization code from user
    auth_code = input("\nEnter the authorization code: ").strip()
    
    if auth_code:
        print(f"\nExchanging code: {auth_code[:10]}...")
        result = exchange_code_for_token(auth_code)
        
        if result:
            print("\n🎉 SUCCESS! You can now use the SMS functionality.")
            print("The token has been saved and will be used automatically.")
        else:
            print("\n❌ Failed to get token. Please try again with a fresh code.")
    else:
        print("No authorization code provided.")

if __name__ == "__main__":
    main() 