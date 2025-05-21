from flask import Flask, request, jsonify
import os
from datetime import datetime
import json

app = Flask(__name__)

# Directory to store webhook data
WEBHOOK_DATA_DIR = 'webhook_data'

# Create directory if it doesn't exist
os.makedirs(WEBHOOK_DATA_DIR, exist_ok=True)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the request body
        data = request.json
        
        # Log the received data
        print("\n=== Received Webhook Data ===")
        print("Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("Contact Info:", data.get('contact', {}))
        print("Conversation Info:", data.get('conversation', {}))
        print("Custom Variables:", data.get('customVariables', {}))
        
        # Save webhook data to a file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{WEBHOOK_DATA_DIR}/webhook_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved webhook data to: {filename}")
        print("===========================\n")
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook data received and stored',
            'file': filename
        })
        
    except Exception as e:
        # Log the error
        print(f"\n=== Error Processing Webhook ===")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Error: {str(e)}")
        print("===========================\n")
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n=== Starting Webhook Server ===")
    print(f"Webhook endpoint: http://localhost:{port}/webhook")
    print("Press Ctrl+C to stop the server")
    print("===============================\n")
    app.run(host='0.0.0.0', port=port) 