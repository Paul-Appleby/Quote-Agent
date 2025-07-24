#!/usr/bin/env python3
"""
GoHighLevel OAuth 2.0 Authorization Script
This script helps you authorize your application with GoHighLevel
"""

import sys
import os
from pathlib import Path

# Add the ghl_tokens directory to the path
sys.path.append(str(Path(__file__).parent / "ghl_tokens"))

from token_handler import start_authorization_flow, exchange_code_for_token

def main():
    print("=" * 60)
    print("GoHighLevel OAuth 2.0 Authorization")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            print("Starting authorization flow...")
            start_authorization_flow()
        elif sys.argv[1] == "exchange":
            if len(sys.argv) > 2:
                code = sys.argv[2]
                print(f"Exchanging authorization code: {code[:10]}...")
                result = exchange_code_for_token(code)
                if result:
                    print("✅ Authorization successful!")
                    print("You can now use the SMS functionality.")
                else:
                    print("❌ Authorization failed!")
            else:
                print("Usage: python authorize_ghl.py exchange <authorization_code>")
        else:
            print("Unknown command. Use 'start' or 'exchange'")
    else:
        print("GoHighLevel OAuth 2.0 Authorization Helper")
        print("\nCommands:")
        print("  start    - Start the authorization flow")
        print("  exchange - Exchange authorization code for token")
        print("\nUsage:")
        print("  1. python authorize_ghl.py start")
        print("  2. Follow the browser flow and copy the authorization code")
        print("  3. python authorize_ghl.py exchange <your_authorization_code>")
        print("\nMake sure your .env file has:")
        print("  API_CLIENT_ID=your_client_id")
        print("  API_CLIENT_SECRET=your_client_secret")
        print("  API_REDIRECT_URI=http://localhost:8080/callback")

if __name__ == "__main__":
    main() 