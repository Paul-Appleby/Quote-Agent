from flask import Flask, request, jsonify
import os
from datetime import datetime
import json
import sys

app = Flask(__name__)

# Store the latest webhook data
latest_webhook_data = None

@app.route('/webhook', methods=['POST'])
def webhook():
    global latest_webhook_data
    try:
        # Get the request body
        data = request.json
        
        # Check if this is a clear request
        if data.get('clear'):
            latest_webhook_data = None
            return jsonify({
                'status': 'success',
                'message': 'Webhook data cleared',
                'data_received': False
            })
        
        # Log the received data
        print("\n=== Received Webhook Data ===", file=sys.stderr)
        print("Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), file=sys.stderr)
        print("Raw Data:", json.dumps(data, indent=2), file=sys.stderr)
        
        # Store the latest webhook data
        latest_webhook_data = data
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook data received',
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

@app.route('/latest_webhook', methods=['GET'])
def get_latest_webhook():
    """Endpoint to get the latest webhook data"""
    if latest_webhook_data:
        return jsonify({
            'status': 'success',
            'data': latest_webhook_data,
            'data_received': True
        })
    else:
        return jsonify({
            'status': 'success',
            'data': None,
            'data_received': False
        })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"\n=== Starting Webhook Server ===", file=sys.stderr)
    print(f"Webhook endpoint: http://localhost:{port}/webhook", file=sys.stderr)
    print("Press Ctrl+C to stop the server", file=sys.stderr)
    print("===============================\n", file=sys.stderr)
    app.run(host='0.0.0.0', port=port) 