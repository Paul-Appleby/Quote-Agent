import sqlite3
import os
from datetime import datetime

def init_db():
    """Initialize the SQLite database and create the conversations table."""
    # Ensure the db directory exists
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'conversations.db'))
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contact_id TEXT NOT NULL,
        sender TEXT CHECK(sender IN ('customer', 'agent')) NOT NULL,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create index on contact_id for faster lookups
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_conversations_contact_id 
    ON conversations(contact_id)
    ''')
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def main():
    """Main function to initialize the database."""
    try:
        init_db()
        print("Database created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    main() 