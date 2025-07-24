from typing import List, Dict
import os
from dotenv import load_dotenv
import openai
from config import get_settings

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
settings = get_settings()

class SalesAgent:
    def __init__(self):
        self.system_prompt = """You are a friendly, professional sales agent for a car detailing business. 
        Your goal is to help customers understand our services and generate quotes when they're ready.
        Always maintain a helpful, conversational tone while gathering necessary information.
        If a customer seems ready for a quote, ask for their car's make, model, and year."""
    
    def format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history into a string for the LLM prompt."""
        formatted_history = []
        for msg in reversed(history):  # Reverse to show oldest messages first
            role = "Customer" if msg['sender'] == 'customer' else "Agent"
            formatted_history.append(f"{role}: {msg['message']}")
        return "\n".join(formatted_history)
    
    def generate_response(self, current_message: str, history: List[Dict]) -> str:
        """
        Generate a response using the conversation history as context.
        
        Args:
            current_message: The latest message from the customer
            history: List of previous messages in the conversation
            
        Returns:
            str: Generated response
        """
        # Format conversation history
        conversation_context = self.format_conversation_history(history)
        
        # Create the full prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Previous conversation:
{conversation_context}

Latest message from customer: {current_message}

Please provide a helpful response that:
1. Addresses the customer's message
2. Maintains context from previous messages
3. Moves the conversation forward naturally
4. Asks for necessary information if they seem ready for a quote"""}
        ]
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble processing your message right now. Please try again in a moment."

# Example usage
if __name__ == "__main__":
    agent = SalesAgent()
    
    # Test conversation
    test_history = [
        {
            "contact_id": "test_123",
            "sender": "customer",
            "message": "Hi, I'm interested in getting my car detailed",
            "timestamp": "2024-03-14T12:00:00Z"
        }
    ]
    
    response = agent.generate_response(
        "What services do you offer?",
        test_history
    )
    print("Generated response:", response) 