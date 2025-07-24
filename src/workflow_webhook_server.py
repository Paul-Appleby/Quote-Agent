from flask import Flask, request, jsonify
import json
from datetime import datetime
from typing import Dict, Any, Optional
from workflow_agent import WorkflowAgent
import os

app = Flask(__name__)

# Initialize the workflow agent
workflow_file = "WAXD Inbound Call - 36e52fcb-543b-40a2-a82e-bb8bd2407dc3.json"
if os.path.exists(workflow_file):
    workflow_agent = WorkflowAgent(workflow_file)
    print(f"✅ Loaded workflow from {workflow_file}")
else:
    workflow_agent = None
    print(f"❌ Workflow file {workflow_file} not found!")

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
    Process an SMS message through the workflow agent
    """
    if not workflow_agent:
        return {
            'success': False,
            'error': 'Workflow agent not initialized'
        }
    
    try:
        # Process through the workflow
        result = workflow_agent.process_message(
            customer_id=customer_id,
            message=message_content,
            pipeline_stage=pipeline_stage
        )
        
        return result
    
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
        
        # Process the message through the workflow agent
        result = process_sms_message(customer_id, message_content, pipeline_stage)
        
        if result['success']:
            print(f"AI Response: {result['response']}")
            print(f"Next Node: {result['next_node']}")
            print(f"Pipeline Stage: {result['pipeline_stage']}")
            
            # TODO: Send SMS response back via GoHighLevel
            # You can integrate with send_ghl_sms.py here
            
            # Return success response
            return jsonify({
                'success': True,
                'ai_response': result['response'],
                'next_node': result['next_node'],
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
        'message': 'Workflow webhook server is running',
        'workflow_loaded': workflow_agent is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/workflow/status', methods=['GET'])
def get_workflow_status():
    """
    Get workflow status and node information
    """
    if not workflow_agent:
        return jsonify({'error': 'Workflow not loaded'}), 500
    
    nodes_info = {}
    for node_id, node in workflow_agent.nodes.items():
        nodes_info[node_id] = {
            'name': node.name,
            'type': node.node_type,
            'has_prompt': bool(node.prompt)
        }
    
    return jsonify({
        'workflow_file': workflow_file,
        'total_nodes': len(workflow_agent.nodes),
        'nodes': nodes_info,
        'global_config': workflow_agent.global_config
    })

@app.route('/workflow/test', methods=['POST'])
def test_workflow():
    """
    Test the workflow with a sample message
    """
    if not workflow_agent:
        return jsonify({'error': 'Workflow not loaded'}), 500
    
    try:
        data = request.get_json()
        customer_id = data.get('customer_id', 'test_customer_123')
        message = data.get('message', 'Hi, I need car detailing')
        pipeline_stage = data.get('pipeline_stage', 'New Lead')
        
        result = workflow_agent.process_message(customer_id, message, pipeline_stage)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting workflow webhook server...")
    print("Webhook endpoint: http://localhost:5001/webhook")
    print("Test endpoint: http://localhost:5001/webhook/test")
    print("Workflow status: http://localhost:5001/workflow/status")
    print("Workflow test: http://localhost:5001/workflow/test")
    
    if workflow_agent:
        print("✅ Workflow agent initialized successfully")
    else:
        print("❌ Workflow agent failed to initialize")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 