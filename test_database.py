#!/usr/bin/env python3
"""
Test script for the simplified sales agent database functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import SalesDatabase

def test_database():
    """Test the simplified database functionality"""
    print("=== Testing Simplified Sales Database ===\n")
    
    # Initialize database
    db = SalesDatabase("test_sales_agent.db")
    
    # Test 1: Create a conversation
    print("1. Creating conversation...")
    conversation_id = db.get_or_create_conversation(
        ghl_customer_id="test_customer_123",
        phone_number="555-1234",
        pipeline_stage="New Lead"
    )
    print(f"   Conversation created with ID: {conversation_id}")
    
    # Test 2: Add messages
    print("\n2. Adding messages...")
    db.add_message(conversation_id, "user", "Hi, I need car detailing")
    db.add_message(conversation_id, "assistant", "Hello! I'd be happy to help you with car detailing. What type of vehicle do you have?")
    db.add_message(conversation_id, "user", "I have a 2020 Honda Civic")
    print("   Messages added successfully")
    
    # Test 3: Get conversation by GHL ID
    print("\n3. Retrieving conversation by GHL ID...")
    conversation = db.get_conversation_by_ghl_id("test_customer_123")
    if conversation:
        print(f"   Found conversation: {conversation['pipeline_stage']} ({conversation['phone_number']})")
    
    # Test 4: Get conversation messages
    print("\n4. Retrieving conversation messages...")
    messages = db.get_conversation_messages(conversation_id)
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. {msg['role']}: {msg['content']}")
    
    # Test 5: Test conversation resumption
    print("\n5. Testing conversation resumption...")
    existing_conversation_id = db.get_or_create_conversation(
        ghl_customer_id="test_customer_123",
        phone_number="555-1234",
        pipeline_stage="Follow-up"
    )
    print(f"   Existing conversation ID returned: {existing_conversation_id}")
    print(f"   Same as original: {existing_conversation_id == conversation_id}")
    
    # Test 6: Create another conversation for different customer
    print("\n6. Creating conversation for different customer...")
    conversation_id_2 = db.get_or_create_conversation(
        ghl_customer_id="test_customer_456",
        phone_number="555-5678",
        pipeline_stage="New Lead"
    )
    print(f"   Second conversation created with ID: {conversation_id_2}")
    
    # Test 7: Get conversation stats
    print("\n7. Getting conversation stats...")
    stats = db.get_conversation_stats()
    print(f"   Unique customers: {stats['unique_customers']}")
    print(f"   Active conversations: {stats['active_conversations']}")
    print(f"   Pipeline breakdown: {stats['pipeline_breakdown']}")
    
    # Test 8: Get conversation history
    print("\n8. Getting conversation history...")
    history = db.get_conversation_history("test_customer_123")
    print(f"   Found {len(history)} conversations for customer")
    for conv in history:
        print(f"   - Conversation {conv['id']}: {conv['pipeline_stage']} (Active: {conv['is_active']})")
    
    print("\n=== Database Test Complete ===")
    print("Database file created: test_sales_agent.db")
    print("You can inspect it with: sqlite3 test_sales_agent.db")

if __name__ == "__main__":
    test_database() 