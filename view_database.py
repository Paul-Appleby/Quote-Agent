#!/usr/bin/env python3
"""
Simple database viewer for the sales agent database
"""

import sqlite3
import json
from tabulate import tabulate
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def view_database(db_path="sales_agent.db"):
    """View database contents in a readable format"""
    
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print(f"DATABASE: {db_path}")
    print("=" * 60)
    
    # Show tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\n📋 TABLES FOUND: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
    
    # View conversations table
    print(f"\n🗂️  CONVERSATIONS TABLE")
    print("-" * 40)
    
    cursor.execute("""
        SELECT id, ghl_customer_id, pipeline_stage, 
               current_node, created_date, last_updated, is_active
        FROM conversations
        ORDER BY created_date DESC
        LIMIT 10
    """)
    
    conversations = cursor.fetchall()
    if conversations:
        headers = ["ID", "GHL Customer ID", "Pipeline Stage", "Current Node", "Created", "Updated", "Active"]
        print(tabulate(conversations, headers=headers, tablefmt="grid"))
    else:
        print("No conversations found.")
    
    # View messages table
    print(f"\n💬 MESSAGES TABLE (Last 10)")
    print("-" * 40)
    
    cursor.execute("""
        SELECT m.id, m.conversation_id, m.role, 
               SUBSTR(m.content, 1, 50) || '...' as content_preview,
               m.timestamp
        FROM messages m
        ORDER BY m.timestamp DESC
        LIMIT 10
    """)
    
    messages = cursor.fetchall()
    if messages:
        headers = ["ID", "Conv ID", "Role", "Content Preview", "Timestamp"]
        print(tabulate(messages, headers=headers, tablefmt="grid"))
    else:
        print("No messages found.")
    
    # Show statistics
    print(f"\n📊 DATABASE STATISTICS")
    print("-" * 40)
    
    # Count conversations
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total_conversations = cursor.fetchone()[0]
    
    # Count active conversations
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE is_active = 1")
    active_conversations = cursor.fetchone()[0]
    
    # Count messages
    cursor.execute("SELECT COUNT(*) FROM messages")
    total_messages = cursor.fetchone()[0]
    
    # Count unique customers
    cursor.execute("SELECT COUNT(DISTINCT ghl_customer_id) FROM conversations")
    unique_customers = cursor.fetchone()[0]
    
    # Pipeline breakdown
    cursor.execute("""
        SELECT pipeline_stage, COUNT(*) 
        FROM conversations 
        WHERE is_active = 1 
        GROUP BY pipeline_stage
    """)
    pipeline_stats = cursor.fetchall()
    
    stats_data = [
        ["Total Conversations", total_conversations],
        ["Active Conversations", active_conversations],
        ["Total Messages", total_messages],
        ["Unique Customers", unique_customers]
    ]
    
    print(tabulate(stats_data, headers=["Metric", "Count"], tablefmt="grid"))
    
    if pipeline_stats:
        print(f"\nPipeline Stage Breakdown:")
        for stage, count in pipeline_stats:
            print(f"  {stage}: {count}")
    
    # Show recent activity
    print(f"\n🕒 RECENT ACTIVITY")
    print("-" * 40)
    
    cursor.execute("""
        SELECT c.ghl_customer_id, c.pipeline_stage, c.last_updated,
               (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count
        FROM conversations c
        WHERE c.is_active = 1
        ORDER BY c.last_updated DESC
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    if recent:
        headers = ["GHL Customer ID", "Pipeline Stage", "Last Updated", "Messages"]
        print(tabulate(recent, headers=headers, tablefmt="grid"))
    else:
        print("No recent activity.")
    
    conn.close()

def view_conversation_details(db_path="sales_agent.db", conversation_id=None):
    """View detailed conversation with messages"""
    
    if not conversation_id:
        print("Please provide a conversation ID")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get conversation details
    cursor.execute("""
        SELECT ghl_customer_id, pipeline_stage, current_node, 
               created_date, last_updated, context
        FROM conversations
        WHERE id = ?
    """, (conversation_id,))
    
    conv_data = cursor.fetchone()
    if not conv_data:
        print(f"Conversation {conversation_id} not found!")
        return
    
    ghl_id, pipeline, node, created, updated, context_json = conv_data
    
    print(f"\n🗂️  CONVERSATION DETAILS - ID: {conversation_id}")
    print("=" * 60)
    print(f"GHL Customer ID: {ghl_id}")
    print(f"Pipeline Stage: {pipeline}")
    print(f"Current Node: {node}")
    print(f"Created: {created}")
    print(f"Last Updated: {updated}")
    
    if context_json:
        try:
            context = json.loads(context_json)
            if context:
                print(f"Context: {json.dumps(context, indent=2)}")
        except:
            print(f"Context: {context_json}")
    
    # Get messages
    cursor.execute("""
        SELECT role, content, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp
    """, (conversation_id,))
    
    messages = cursor.fetchall()
    
    print(f"\n💬 MESSAGES ({len(messages)} total)")
    print("-" * 60)
    
    for i, (role, content, timestamp) in enumerate(messages, 1):
        role_icon = "👤" if role == "user" else "🤖"
        print(f"{i}. {role_icon} {role.upper()} ({timestamp})")
        print(f"   {content}")
        print()
    
    conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View sales agent database")
    parser.add_argument("--db", default="sales_agent.db", help="Database file path")
    parser.add_argument("--conversation", type=int, help="View specific conversation details")
    
    args = parser.parse_args()
    
    if args.conversation:
        view_conversation_details(args.db, args.conversation)
    else:
        view_database(args.db) 