import requests
import json

url = "https://services.leadconnectorhq.com/oauth/token"

payload = {
    "client_id": "6835011c08f18f1088f92f9f-mcnl7omh",
    "client_secret": "81c57499-1041-494a-9d59-7ecf3914b191",
    "grant_type": "authorization_code",
    "code": "1bc5cb49744d4544a1e79057e6e24dc108e3e735",
    "redirect_uri": "https://github.com"
}

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

print("Sending OAuth token request...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print(f"Headers: {json.dumps(headers, indent=2)}")

response = requests.post(url, data=payload, headers=headers)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Body: {response.text}")

if response.status_code == 200:
    print("\n✅ SUCCESS! Token received:")
    token_data = response.json()
    print(json.dumps(token_data, indent=2))
else:
    print(f"\n❌ ERROR: {response.status_code}")
    error_data = response.json()
    print(json.dumps(error_data, indent=2))
    
    # Provide helpful error messages
    if error_data.get('error') == 'invalid_grant':
        print("\n💡 This usually means:")
        print("1. The authorization code has expired (they expire quickly)")
        print("2. The authorization code has already been used")
        print("3. The redirect_uri doesn't match what was used to get the code")
        print("\nYou need to get a fresh authorization code from GoHighLevel.")
