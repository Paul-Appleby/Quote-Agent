from flask import Flask, request, jsonify
import json
from datetime import datetime
from typing import Dict, Any, Optional
from database import SalesDatabase
from agent import ConversationState, graph

app = Flask(__name__)
db = SalesDatabase()

def extract_webhook_data(payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Extract customer ID, SMS content, and pipeline stage from GoHighLevel webhook payload
    """
    try:
        # Extract customer ID
        customer_id = payload.get('customerId')
        if not customer_id:
            print("No customerId found in webhook payload")
            return None
        
        # Extract SMS content
        message_content = payload.get('message', {}).get('content', '')
        if not message_content:
            print("No message content found in webhook payload")
            return None
        
        # Extract pipeline stage (with fallback to default)
        pipeline_stage = payload.get('pipeline_stage', 'New Lead')
        
        # Extract customer name (optional)
        customer_name = payload.get('customer', {}).get('firstName', '')
        if customer_name:
            last_name = payload.get('customer', {}).get('lastName', '')
            if last_name:
                customer_name += f" {last_name}"
        
        return {
            'customer_id': customer_id,
            'message_content': message_content,
            'pipeline_stage': pipeline_stage,
            'customer_name': customer_name
        }
    
    except Exception as e:
        print(f"Error extracting webhook data: {e}")
        return None

def process_sms_message(customer_id: str, message_content: str, pipeline_stage: str = "New Lead") -> Dict[str, Any]:
    """
    Process an SMS message through the sales agent workflow
    """
    try:
        # Get or create conversation with pipeline stage
        conversation_id = db.get_or_create_conversation(customer_id, pipeline_stage)
        
        # Load existing state or create new one
        current_state = db.load_conversation_state(conversation_id)
        if not current_state:
            # Only create new state if no existing conversation
            current_state = ConversationState.create_new(
                customer_id=customer_id,
                pipeline_stage=pipeline_stage
            )
        
        # Add the incoming message to context
        current_state.context["current_message"] = message_content
        
        # Process through the graph - this will continue from current_node
        result = graph.invoke(current_state)
        
        # Update state - the graph returns {"state": updated_state}
        current_state = result["state"]
        
        # Save to database
        db.save_conversation_state(conversation_id, current_state)
        
        # Get the AI response
        ai_response = ""
        for msg in reversed(current_state.messages):
            if msg["role"] == "assistant":
                ai_response = msg["content"]
                break
        
        return {
            'success': True,
            'conversation_id': conversation_id,
            'ai_response': ai_response,
            'pipeline_stage': current_state.pipeline_stage,
            'current_node': current_state.current_node
        }
    
    except Exception as e:
        print(f"Error processing SMS message: {e}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/webhook', methods=['POST'])
def handle_sms_webhook():
    """
    Handle incoming SMS webhook from GoHighLevel
    """
    try:
        # Get the webhook payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No payload received'}), 400
        
        print(f"Received webhook payload: {json.dumps(payload, indent=2)}")
        
        # Extract data from webhook
        webhook_data = extract_webhook_data(payload)
        if not webhook_data:
            return jsonify({'error': 'Invalid webhook data'}), 400
        
        customer_id = webhook_data['customer_id']
        message_content = webhook_data['message_content']
        pipeline_stage = webhook_data['pipeline_stage']
        customer_name = webhook_data['customer_name']
        
        print(f"Processing SMS from {customer_name}: {message_content}")
        
        # Process the message through the sales agent
        result = process_sms_message(customer_id, message_content, pipeline_stage)
        
        if result['success']:
            print(f"AI Response: {result['ai_response']}")
            print(f"Pipeline Stage: {result['pipeline_stage']}")
            
            # Return success response
            return jsonify({
                'success': True,
                'ai_response': result['ai_response'],
                'conversation_id': result['conversation_id'],
                'pipeline_stage': result['pipeline_stage']
            })
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/test', methods=['GET'])
def test_webhook():
    """
    Test endpoint to verify webhook server is running
    """
    return jsonify({
        'status': 'ok',
        'message': 'Webhook server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/conversations/<customer_id>', methods=['GET'])
def get_conversation_history(customer_id: str):
    """
    Get conversation history for a customer
    """
    try:
        history = db.get_conversation_history(customer_id)
        return jsonify({
            'customer_id': customer_id,
            'conversations': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Get conversation statistics
    """
    try:
        stats = db.get_conversation_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting webhook server...")
    print("Webhook endpoint: http://localhost:5000/webhook")
    print("Test endpoint: http://localhost:5000/webhook/test")
    print("Stats endpoint: http://localhost:5000/stats")
    app.run(host='0.0.0.0', port=5000, debug=True)