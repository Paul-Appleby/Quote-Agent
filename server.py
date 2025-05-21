from flask import Flask, request, jsonify
import os
from datetime import datetime
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the request body
        data = request.json
        
        # Log the received data
        print("\n=== Received Webhook Data ===")
        print("Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("Contact Info:", json.dumps(data.get('contact', {}), indent=2))
        print("Conversation Info:", json.dumps(data.get('conversation', {}), indent=2))
        print("Custom Variables:", json.dumps(data.get('customVariables', {}), indent=2))
        
        # Save webhook data to a file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'webhook_{timestamp}.json'
        
        # Use /tmp directory which is writable in cloud environments
        filepath = os.path.join('/tmp', filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved webhook data to: {filepath}")
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