from sales_agent import SalesAgent
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_test_conversation():
    agent = SalesAgent()
    
    # Initial conversation history
    history = [
        {
            "contact_id": "test_123",
            "sender": "customer",
            "message": "Hi, I'm interested in getting my car detailed",
            "timestamp": "2024-03-14T12:00:00Z"
        }
    ]
    
    # Test messages
    test_messages = [
        "What services do you offer?",
        "How much does a basic wash cost?",
        "I have a 2020 Toyota Camry",
        "Yes, I'd like to get a quote"
    ]
    
    print("\n=== Starting Test Conversation ===\n")
    
    # Process each test message
    for message in test_messages:
        print(f"\nCustomer: {message}")
        
        # Generate response
        response = agent.generate_response(message, history)
        print(f"\nAgent: {response}")
        
        # Update history
        history.append({
            "contact_id": "test_123",
            "sender": "customer",
            "message": message,
            "timestamp": "2024-03-14T12:00:00Z"
        })
        history.append({
            "contact_id": "test_123",
            "sender": "agent",
            "message": response,
            "timestamp": "2024-03-14T12:00:00Z"
        })
    
    print("\n=== Test Conversation Complete ===\n")

if __name__ == "__main__":
    run_test_conversation() 