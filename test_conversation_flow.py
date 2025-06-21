#!/usr/bin/env python3
"""
Test script to simulate a conversation flow with multiple SMS messages
"""

import requests
import json
import time

# Test conversation flow
conversation_messages = [
    {
        "customerId": "8mrENnBig20f0h6gNDvR",
        "message": {"content": "Hi, I need car detailing"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "pipeline_stage": "New Lead"
    },
    {
        "customerId": "8mrENnBig20f0h6gNDvR", 
        "message": {"content": "I have a 2020 Honda Civic"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "pipeline_stage": "New Lead"
    },
    {
        "customerId": "8mrENnBig20f0h6gNDvR",
        "message": {"content": "It has some scratches and dirt on the seats"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "pipeline_stage": "New Lead"
    },
    {
        "customerId": "8mrENnBig20f0h6gNDvR",
        "message": {"content": "Yes, I'm interested in getting it detailed"},
        "customer": {"firstName": "John", "lastName": "Doe"},
        "pipeline_stage": "New Lead"
    }
]

def test_conversation_flow():
    """Test a conversation flow with multiple messages"""
    
    webhook_url = "http://localhost:5000/webhook"
    
    print("=== Testing Conversation Flow ===")
    print("This will simulate a customer sending multiple SMS messages")
    print("-" * 50)
    
    for i, payload in enumerate(conversation_messages, 1):
        print(f"\n📱 Message {i}: {payload['message']['content']}")
        print("-" * 30)
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ AI Response: {result.get('ai_response', 'No response')}")
                print(f"📍 Current Node: {result.get('current_node', 'Unknown')}")
                print(f"📊 Pipeline Stage: {result.get('pipeline_stage', 'Unknown')}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Small delay between messages
        time.sleep(1)
    
    print("\n=== Conversation Flow Complete ===")
    print("Check the database to see the conversation history!")

if __name__ == "__main__":
    test_conversation_flow() 