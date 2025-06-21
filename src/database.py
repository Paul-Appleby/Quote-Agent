import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import asdict, dataclass

# Define ConversationState structure here to avoid circular import
@dataclass
class ConversationState:
    messages: List[Dict[str, str]]  # List of message dictionaries
    current_node: str               # Current node in the workflow
    pipeline_stage: str            # Current pipeline stage
    context: Dict[str, Any]        # Additional context
    last_updated: datetime         # Timestamp of last update
    customer_id: str = None        # GHL Customer ID

class SalesDatabase:
    def __init__(self, db_path: str = "sales_agent.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table (simplified - no customer table needed)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ghl_customer_id TEXT,
                    pipeline_stage TEXT,
                    current_node TEXT,
                    context TEXT,  -- JSON string
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    role TEXT,  -- 'user' or 'assistant'
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            ''')
            
            conn.commit()
    
    def get_or_create_conversation(self, ghl_customer_id: str, pipeline_stage: str = "New Lead") -> int:
        """Get active conversation or create new one, returns conversation ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check for active conversation
            cursor.execute('''
                SELECT id FROM conversations 
                WHERE ghl_customer_id = ? AND is_active = 1
                ORDER BY last_updated DESC 
                LIMIT 1
            ''', (ghl_customer_id,))
            
            existing = cursor.fetchone()
            if existing:
                conversation_id = existing[0]
                # Update last contact date
                cursor.execute('''
                    UPDATE conversations 
                    SET last_updated = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (conversation_id,))
                return conversation_id
            
            # Create new conversation
            cursor.execute('''
                INSERT INTO conversations (ghl_customer_id, pipeline_stage, current_node, context)
                VALUES (?, ?, ?, ?)
            ''', (ghl_customer_id, pipeline_stage, "sms_handler_node", json.dumps({})))
            
            return cursor.lastrowid
    
    def add_message(self, conversation_id: int, role: str, content: str):
        """Add a message to a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
            ''', (conversation_id, role, content))
    
    def update_conversation_state(self, conversation_id: int, pipeline_stage: str, current_node: str, context: Dict[str, Any]):
        """Update conversation state"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE conversations 
                SET pipeline_stage = ?, current_node = ?, context = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (pipeline_stage, current_node, json.dumps(context), conversation_id))
    
    def get_conversation_messages(self, conversation_id: int) -> List[Dict[str, str]]:
        """Get all messages for a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT role, content, timestamp 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY timestamp
            ''', (conversation_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2]
                })
            
            return messages
    
    def load_conversation_state(self, conversation_id: int) -> Optional[ConversationState]:
        """Load a ConversationState from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get conversation details
            cursor.execute('''
                SELECT pipeline_stage, current_node, context, ghl_customer_id
                FROM conversations
                WHERE id = ?
            ''', (conversation_id,))
            
            conv_data = cursor.fetchone()
            if not conv_data:
                return None
            
            pipeline_stage, current_node, context_json, ghl_customer_id = conv_data
            
            # Get messages
            messages = self.get_conversation_messages(conversation_id)
            
            # Create ConversationState
            state = ConversationState(
                messages=messages,
                current_node=current_node,
                pipeline_stage=pipeline_stage,
                context=json.loads(context_json),
                last_updated=datetime.now(),
                customer_id=ghl_customer_id
            )
            
            return state
    
    def save_conversation_state(self, conversation_id: int, state: ConversationState):
        """Save a ConversationState to database"""
        # Update conversation state
        self.update_conversation_state(
            conversation_id, 
            state.pipeline_stage, 
            state.current_node, 
            state.context
        )
        
        # Add any new messages
        if state.messages:
            # Get existing messages to avoid duplicates
            existing_messages = self.get_conversation_messages(conversation_id)
            existing_count = len(existing_messages)
            
            # Add only new messages
            for message in state.messages[existing_count:]:
                self.add_message(conversation_id, message["role"], message["content"])
    
    def get_conversation_by_ghl_id(self, ghl_customer_id: str) -> Optional[Dict]:
        """Get conversation by GHL customer ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, ghl_customer_id, pipeline_stage, current_node, 
                       created_date, last_updated, is_active
                FROM conversations 
                WHERE ghl_customer_id = ? AND is_active = 1
                ORDER BY last_updated DESC
                LIMIT 1
            ''', (ghl_customer_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "ghl_customer_id": row[1],
                    "pipeline_stage": row[2],
                    "current_node": row[3],
                    "created_date": row[4],
                    "last_updated": row[5],
                    "is_active": row[6]
                }
            return None
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get basic conversation statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Active conversations
            cursor.execute('SELECT COUNT(*) FROM conversations WHERE is_active = 1')
            active_conversations = cursor.fetchone()[0]
            
            # Total conversations
            cursor.execute('SELECT COUNT(*) FROM conversations')
            total_conversations = cursor.fetchone()[0]
            
            # Unique customers (by GHL ID)
            cursor.execute('SELECT COUNT(DISTINCT ghl_customer_id) FROM conversations')
            unique_customers = cursor.fetchone()[0]
            
            # Pipeline stage breakdown
            cursor.execute('''
                SELECT pipeline_stage, COUNT(*) 
                FROM conversations 
                WHERE is_active = 1 
                GROUP BY pipeline_stage
            ''')
            pipeline_breakdown = dict(cursor.fetchall())
            
            return {
                "unique_customers": unique_customers,
                "active_conversations": active_conversations,
                "total_conversations": total_conversations,
                "pipeline_breakdown": pipeline_breakdown
            }
    
    def get_conversation_history(self, ghl_customer_id: str) -> List[Dict]:
        """Get all conversations for a customer"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, pipeline_stage, created_date, last_updated, is_active
                FROM conversations 
                WHERE ghl_customer_id = ?
                ORDER BY created_date DESC
            ''', (ghl_customer_id,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    "id": row[0],
                    "pipeline_stage": row[1],
                    "created_date": row[2],
                    "last_updated": row[3],
                    "is_active": row[4]
                })
            
            return conversations 