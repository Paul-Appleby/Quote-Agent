import openai
import langchain
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import getpass
import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
# Load environment variables and set API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import and initialize the chat model
from langchain.chat_models import init_chat_model
model = init_chat_model("gpt-3.5-turbo", model_provider="openai")

# Define how the AI should behave
system_template = "You are a sales agent for WAXD Car Detailing Austin. Respond to the user's message in a friendly and professional manner."

# Create a template for conversations
prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),  # Sets the AI's role
    ("user", "{input}")          # Placeholder for user input
])

# Main conversation loop
def main():
    while True:
        try:
        # Get user input
            user_input = input("Message from user: ")
            
        # Format the messages using our template
            messages = prompt.format_messages(input=user_input)
        
        # Get AI's response
            response = model.invoke(messages)
        
        # Print the response with a separator
            print("Response:", response.content)

        except EOFError:
            print("Exiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

main()