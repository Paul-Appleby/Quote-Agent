#!/usr/bin/env python3
"""
Test script for the WAXD workflow system
"""

import requests
import json
import time

def test_workflow_server():
    """Test if the workflow server is running"""
    
    test_url = "http://localhost:5001/webhook/test"
    
    try:
        response = requests.get(test_url, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Workflow server is running!")
            print(f"Status: {result.get('status')}")
            print(f"Workflow loaded: {result.get('workflow_loaded')}")
            return True
        else:
            print("❌ Workflow server returned error status")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Workflow server is not running")
        print("Start it with: python src/workflow_webhook_server.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def test_workflow_status():
    """Test the workflow status endpoint"""
    
    status_url = "http://localhost:5001/workflow/status"
    
    try:
        response = requests.get(status_url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("\n=== Workflow Status ===")
            print(f"Workflow file: {result.get('workflow_file')}")
            print(f"Total nodes: {result.get('total_nodes')}")
            print(f"Global config: {result.get('global_config', {}).get('globalPrompt', 'No global prompt')[:100]}...")
            
            print("\n=== Nodes ===")
            for node_id, node_info in result.get('nodes', {}).items():
                print(f"  {node_id}: {node_info['name']} ({node_info['type']})")
            
            return True
        else:
            print(f"❌ Error getting workflow status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_workflow_conversation():
    """Test a conversation through the workflow"""
    
    test_url = "http://localhost:5001/workflow/test"
    
    # Test conversation messages
    test_messages = [
        {
            "customer_id": "test_customer_123",
            "message": "Hi, I need car detailing for my Honda Civic",
            "pipeline_stage": "New Lead"
        },
        {
            "customer_id": "test_customer_123", 
            "message": "Yes, it's pretty dirty. I want a full detail",
            "pipeline_stage": "New Lead"
        },
        {
            "customer_id": "test_customer_123",
            "message": "How much does it cost?",
            "pipeline_stage": "New Lead"
        }
    ]
    
    print("\n=== Testing Workflow Conversation ===")
    
    for i, test_data in enumerate(test_messages, 1):
        print(f"\n📱 Message {i}: {test_data['message']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                test_url,
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ AI Response: {result.get('response', 'No response')}")
                    print(f"📍 Next Node: {result.get('next_node', 'Unknown')}")
                    print(f"📊 Pipeline Stage: {result.get('pipeline_stage', 'Unknown')}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between messages
        time.sleep(1)

def test_webhook_endpoint():
    """Test the webhook endpoint with a realistic payload"""
    
    webhook_url = "http://localhost:5001/webhook"
    
    # Simulate GoHighLevel webhook payload
    webhook_payload = {
        "customerId": "8mrENnBig20f0h6gNDvR",
        "message": {
            "content": "Hi, I need car detailing for my Honda Civic",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        "customer": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com"
        },
        "pipeline_stage": "New Lead",
        "locationId": "test_location_123",
        "userId": "test_user_456"
    }
    
    print("\n=== Testing Webhook Endpoint ===")
    print(f"Payload: {json.dumps(webhook_payload, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=webhook_payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook test successful!")
            print(f"AI Response: {result.get('ai_response', 'No response')}")
            print(f"Next Node: {result.get('next_node', 'Unknown')}")
            print(f"Pipeline Stage: {result.get('pipeline_stage', 'Unknown')}")
            print(f"Conversation ID: {result.get('conversation_id', 'Unknown')}")
        else:
            print("❌ Webhook test failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests"""
    print("=== WAXD Workflow System Test ===")
    
    # Test 1: Check if server is running
    if not test_workflow_server():
        return
    
    # Test 2: Check workflow status
    if not test_workflow_status():
        return
    
    # Test 3: Test workflow conversation
    test_workflow_conversation()
    
    # Test 4: Test webhook endpoint
    test_webhook_endpoint()
    
    print("\n=== Test Complete ===")
    print("Check the database to see conversation history!")

if __name__ == "__main__":
    main() 