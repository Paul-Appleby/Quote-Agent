import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'conversations.db')
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def store_message(self, contact_id: str, message: str, sender: str = 'customer') -> bool:
        """
        Store a new message in the database.
        
        Args:
            contact_id: The GHL contact ID
            message: The message content
            sender: Either 'customer' or 'agent'
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO conversations (contact_id, sender, message)
            VALUES (?, ?, ?)
            ''', (contact_id, sender, message))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing message: {e}")
            return False
    
    def get_conversation_history(self, contact_id: str, limit: int = 10) -> List[Dict]:
        """
        Retrieve conversation history for a specific contact.
        
        Args:
            contact_id: The GHL contact ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of dictionaries containing message data
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, contact_id, sender, message, timestamp
            FROM conversations
            WHERE contact_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            ''', (contact_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'contact_id': row[1],
                    'sender': row[2],
                    'message': row[3],
                    'timestamp': row[4]
                })
            
            conn.close()
            return messages
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []
    
    def get_last_message(self, contact_id: str) -> Optional[Dict]:
        """
        Get the most recent message for a contact.
        
        Args:
            contact_id: The GHL contact ID
            
        Returns:
            Dictionary containing the last message data or None if no messages exist
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, contact_id, sender, message, timestamp
            FROM conversations
            WHERE contact_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            ''', (contact_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'contact_id': row[1],
                    'sender': row[2],
                    'message': row[3],
                    'timestamp': row[4]
                }
            return None
        except Exception as e:
            print(f"Error retrieving last message: {e}")
            return None

# Example usage:
if __name__ == "__main__":
    db = DatabaseManager()
    
    # Store a test message
    db.store_message("test_contact_123", "Hello, this is a test message!")
    
    # Get conversation history
    history = db.get_conversation_history("test_contact_123")
    print("Conversation history:", history)
    
    # Get last message
    last_msg = db.get_last_message("test_contact_123")
    print("Last message:", last_msg) 