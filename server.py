from flask import Flask, request, jsonify
import os
from datetime import datetime
import json
import sys

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Get the request body
        data = request.json
        
        # Log the received data
        print("\n=== Received Webhook Data ===", file=sys.stderr)
        print("Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), file=sys.stderr)
        print("Raw Data:", json.dumps(data, indent=2), file=sys.stderr)
        
        # Save webhook data to a file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'webhook_{timestamp}.json'
        
        # Use /tmp directory which is writable in cloud environments
        filepath = os.path.join('/tmp', filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved webhook data to: {filepath}", file=sys.stderr)
        print("===========================\n", file=sys.stderr)
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook data received and stored',
            'file': filename,
            'data_received': True
        })
        
    except Exception as e:
        # Log the error
        print(f"\n=== Error Processing Webhook ===", file=sys.stderr)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=sys.stderr)
        print(f"Error: {str(e)}", file=sys.stderr)
        print(f"Request Data: {request.get_data()}", file=sys.stderr)
        print("===========================\n", file=sys.stderr)
        
        return jsonify({
            'status': 'error',
            'message': str(e),
            'data_received': False
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n=== Starting Webhook Server ===", file=sys.stderr)
    print(f"Webhook endpoint: http://localhost:{port}/webhook", file=sys.stderr)
    print("Press Ctrl+C to stop the server", file=sys.stderr)
    print("===============================\n", file=sys.stderr)
    app.run(host='0.0.0.0', port=port) 