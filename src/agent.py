import openai
import langchain
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import getpass
import os
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, START
from database import SalesDatabase

# Load environment variables and set API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@dataclass
class ConversationState:
    messages: List[Dict[str, str]]  # List of message dictionaries
    current_node: str               # Current node in the workflow
    pipeline_stage: str            # Current pipeline stage
    context: Dict[str, Any]        # Additional context
    last_updated: datetime         # Timestamp of last update
    customer_id: str = None        # GHL Customer ID

    @classmethod
    def create_new(cls, pipeline_stage: str = "New Lead", customer_id: str = None):
        return cls(
            messages=[],
            current_node="sms_handler_node",
            pipeline_stage=pipeline_stage,
            context={},
            last_updated=datetime.now(),
            customer_id=customer_id
        )

# Define how the AI should behave
system_template = """You are a sales agent for WAXD Car Detailing Austin. 
Your goal is to help customers book detailing services while maintaining a friendly and professional conversation.
Keep track of the conversation context and use it to provide personalized responses.
Current pipeline stage: {pipeline_stage}
Current node: {current_node}
"""

def format_conversation_history(state: ConversationState) -> str:
    """Format conversation history for the prompt"""
    history = []
    for msg in state.messages[-5:]:  # Keep last 5 messages for context
        if msg["role"] == "user":
            history.append(f"Customer: {msg['content']}")
        else:
            history.append(f"Agent: {msg['content']}")
    return "\n".join(history)

def generate_response(state: ConversationState, custom_system_prompt: str = None) -> str:
    """Generate AI response based on conversation history and context"""
    # Format conversation history
    history = format_conversation_history(state)
    
    # Use custom system prompt if provided, otherwise use default
    system_prompt = custom_system_prompt or system_template
    
    # Create prompt with context
    messages = [
        SystemMessage(content=system_prompt.format(
            pipeline_stage=state.pipeline_stage,
            current_node=state.current_node
        )),
        HumanMessage(content=f"Conversation history:\n{history}\n\nCurrent message: {state.context.get('current_message', '')}")
    ]
    
    # Generate response
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    response = chat.invoke(messages)
    return response.content

# add routing logic - based on pipeline stage and conversation history
def sms_handler_node(state: ConversationState) -> Dict:
    """Handle incoming SMS messages"""
    print("Entering sms handler node")
    
    # Get the current message from context
    current_message = state.context.get("current_message", "")
    
    # Add user message to history
    state.messages.append({
        "role": "user",
        "content": current_message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Initialize sales conditions if not present
    if "has_car_condition" not in state.context:
        state.context["has_car_condition"] = False
    
    # Pass to sales node
    return {"next": "sales_node", "state": state}

def sales_node(state: ConversationState) -> Dict:
    """Handle sales conversation"""
    print("Entering sales node")
    
    # Get current message
    current_message = state.context.get("current_message", "").lower()
    
    # Create a sales-specific system prompt
    sales_system_prompt = """You are a sales agent for WAXD Car Detailing Austin. 
    Your goal is to help customers book detailing services while maintaining a friendly and professional conversation.
    Current pipeline stage: {pipeline_stage}
    Current node: {current_node}
    
    Your primary goal is to get information about the car's condition.
    If you haven't asked about the car's condition yet, ask about it now.
    If you have asked but haven't received a detailed response, ask for more specific details.
    Only move to booking when you have received specific details about the car's condition.
    Keep responses focused on understanding the car's current state.
    """
    
    # Generate sales-focused response
    response = generate_response(state, sales_system_prompt)
    
    # Add AI response to history
    state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })
    
    # Check if we have car condition information
    if not state.context.get("has_car_condition", False) and len(current_message) > 10:  # Basic check for meaningful response
        state.context["has_car_condition"] = True
        state.context["car_condition_details"] = current_message
        print("Car condition received:", current_message)
    
    # Only move to booking if we have car condition AND customer shows interest
    has_car_condition = state.context.get("has_car_condition", False)
    shows_interest = any(word in current_message for word in ["yes", "interested", "book", "schedule", "price", "quote"])
    
    if has_car_condition and shows_interest:
        print("Customer qualified - moving to booking")
        return {"next": "booking_node", "state": state}
    
    # Stay in sales node until we get car condition and interest
    print("Staying in sales node - need more info or interest")
    return {"next": "sales_node", "state": state}


def booking_node(state: ConversationState) -> Dict:
    """Handle booking conversation"""
    print("Entering booking node")
    
    # Generate booking-focused response
    response = generate_response(state)
    
    # Add AI response to history
    state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })
    
    return {"next": END, "state": state}

# Build the graph
builder = StateGraph(ConversationState)
builder.add_node("sms_handler_node", sms_handler_node)
builder.add_node("sales_node", sales_node)
builder.add_node("booking_node", booking_node)

# Add the START edge
builder.add_edge(START, "sms_handler_node")
builder.add_edge("sms_handler_node", "sales_node")
builder.add_edge("sales_node", "booking_node")
builder.add_edge("booking_node", END)

graph = builder.compile()

def main():
    """Main conversation loop with database integration"""
    print("Starting conversation with WAXD agent...")
    print("Type 'exit' to end the conversation")
    
    # Initialize database
    db = SalesDatabase()
    
    # Get GHL customer ID for this session
    ghl_customer_id = "8mrENnBig20f0h6gNDvR"
    
    # Check if there's an existing conversation
    existing_conversation = db.get_conversation_by_ghl_id(ghl_customer_id)
    if existing_conversation:
        print(f"Found existing conversation from: {existing_conversation['pipeline_stage']}")
        conversation_id = existing_conversation['id']
        current_state = db.load_conversation_state(conversation_id)
        if not current_state:
            print("Error loading conversation, starting new one...")
            conversation_id = db.get_or_create_conversation(ghl_customer_id)
            current_state = ConversationState.create_new(customer_id=ghl_customer_id)
    else:
        print("Starting new conversation...")
        conversation_id = db.get_or_create_conversation(ghl_customer_id)
        current_state = ConversationState.create_new(customer_id=ghl_customer_id)
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                print("Ending conversation...")
                break
            
            # Update state with new message
            current_state.context["current_message"] = user_input
            
            # Process through graph
            result = graph.invoke(current_state)
            
            # Update state
            current_state = result["state"]
            
            # Save to database
            db.save_conversation_state(conversation_id, current_state)
            
            # Print the last AI response
            for msg in reversed(current_state.messages):
                if msg["role"] == "assistant":
                    print(f"\nAgent: {msg['content']}")
                    break
            
            print(f"Current node: {current_state.current_node}")
            print(f"Pipeline stage: {current_state.pipeline_stage}")
            if current_state.customer_id:
                print(f"Customer ID: {current_state.customer_id}")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    
    # Show conversation stats
    stats = db.get_conversation_stats()
    print(f"\n=== Session Stats ===")
    print(f"Unique customers: {stats['unique_customers']}")
    print(f"Active conversations: {stats['active_conversations']}")
    print(f"Pipeline breakdown: {stats['pipeline_breakdown']}")

if __name__ == "__main__":
    main()