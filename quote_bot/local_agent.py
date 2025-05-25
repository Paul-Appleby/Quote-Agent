import requests
import json
import time
import asyncio
import sys
import os
from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables with error checking
FIELDD_USERNAME = os.getenv('FIELDD_USERNAME')
FIELDD_PASSWORD = os.getenv('FIELDD_PASSWORD')
COMPANY_CITY = os.getenv('COMPANY_CITY')

# Verify environment variables are loaded
if not all([FIELDD_USERNAME, FIELDD_PASSWORD, COMPANY_CITY]):
    print("Error: Missing required environment variables. Please check your .env file contains:", file=sys.stderr)
    print("FIELDD_USERNAME=your_username", file=sys.stderr)
    print("FIELDD_PASSWORD=your_password", file=sys.stderr)
    print("COMPANY_CITY=your_city", file=sys.stderr)
    sys.exit(1)

# Base system message template
extend_system_message = """
When creating a quote in Fieldd CRM:
1. Navigate to https://admin.fieldd.co/#!/company/schedule/planner
2. Log into fieldd: 
   - Enter email using the "email" login field:
   - Username: {FIELDD_USERNAME}
   - Hit the "next" arrow button to open the password field
   - Enter password using the "password" login field:
   - Password: {FIELDD_PASSWORD}
   - Login
3. Once logged in, locate the "new" button, with button id="add-button" and text "New" and then, within the dropdown menu, select "quote"
4. In the "Customer" section:
    First name (with ng-model="formData.customerFirstName"): {first_name}
    Last name (with ng-model="formData.customerLastName"): {last_name}
    Address field instructions:
    - Find input field with ng-model="formData.customerAddress"
    - Type "{customer_address}" AND wait for dropdown
    - Look for dropdown items with class="ui-select-choices-row"
    - Select the item that contains "{COMPANY_CITY}"
    - If dropdown doesn't appear:
      * Try clicking the field first
      * If still no dropdown, try typing the address slowly
    - Verify the address is selected correctly
    Email (with ng-model="formData.customerEmail"): {customer_email}
    Phone (with ng-model="viewData.customerPhone"): {customer_phone}
    - Verify all customer information is saved correctly
5. In the "Job Address" section:
    - Find input field with ng-model="formData.jobAddress" and data-onchange="onJobAddressSelect"
    - Enter: {customer_address}
    - Wait for dropdown
    - Look for dropdown items with class="ui-select-choices-row"
    - Select the item that contains "{COMPANY_CITY}"
    - If dropdown doesn't appear, try clicking the field first
    - If still no dropdown, try typing the address slowly
    - Verify the job address is selected correctly
6. Under "acceptance" select "self schedule"
7. In the "Service Selection" section:
    - Find the div with class="service-selection-left"
    - Within that div, find the input field with ng-model="item.name"
    - Type "{service_request}" and wait for dropdown
    - In the dropdown, look for a package that matches both:
      * The service name "{service_request}"
      * The car size "{car_size}"
    - Select the matching package
    - Verify the correct package is selected
8. Select "send quote"
9. If quote fails:
    - Look for the error message
    - Try to fix any address validation issues
    - If still failing, report the error message
"""

# Format only the environment variables in the system message
extend_system_message = extend_system_message.replace("{FIELDD_USERNAME}", FIELDD_USERNAME)
extend_system_message = extend_system_message.replace("{FIELDD_PASSWORD}", FIELDD_PASSWORD)
extend_system_message = extend_system_message.replace("{COMPANY_CITY}", COMPANY_CITY)

def clear_webhook_data():
    """Clear any existing webhook data when starting up"""
    try:
        print("\nClearing any existing webhook data...", file=sys.stderr)
        # Send empty data to clear the webhook
        response = requests.post(
            'https://ghlwebhook-production.up.railway.app/webhook',
            json={"clear": True}
        )
        if response.status_code == 200:
            print("Webhook data cleared successfully", file=sys.stderr)
        else:
            print(f"Warning: Could not clear webhook data. Status code: {response.status_code}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Error clearing webhook data: {str(e)}", file=sys.stderr)

async def run_automation(data):
    try:
        print("\n=== Starting Automation ===", file=sys.stderr)
        
        # Print raw data for debugging
        print("\n=== Raw Webhook Data ===", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        
        # Extract customer info from custom Quote_ fields
        custom_data = data.get('customData', {})
        customer_data = {
            'first_name': custom_data.get('Quote_First_Name', ''),
            'last_name': custom_data.get('Quote_Last_Name', ''),
            'email': custom_data.get('Quote_Email', ''),
            'phone': custom_data.get('Quote_Phone', ''),
            'address': custom_data.get('Quote_Address', ''),
            'service_request': custom_data.get('Quote_Package', ''),
            'car_size': custom_data.get('Quote_Car_Size', '')
        }
        
        # Print extracted data
        print("\n=== Extracted Webhook Data ===", file=sys.stderr)
        print("First Name:", customer_data.get('first_name', 'Not found'), file=sys.stderr)
        print("Last Name:", customer_data.get('last_name', 'Not found'), file=sys.stderr)
        print("Customer Email:", customer_data.get('email', 'Not found'), file=sys.stderr)
        print("Customer Phone:", customer_data.get('phone', 'Not found'), file=sys.stderr)
        print("Customer Address:", customer_data.get('address', 'Not found'), file=sys.stderr)
        print("Service Request:", customer_data.get('service_request', 'Not found'), file=sys.stderr)
        print("Car Size:", customer_data.get('car_size', 'Not found'), file=sys.stderr)
        
        # Ask for confirmation
        # input("\nPress Enter to proceed with quote creation using this data...")
        
        # Format the system message with customer data
        formatted_message = extend_system_message.format(
            first_name=customer_data['first_name'],
            last_name=customer_data['last_name'],
            customer_email=customer_data['email'],
            customer_phone=customer_data['phone'],
            customer_address=customer_data['address'],
            service_request=customer_data['service_request'],
            car_size=customer_data['car_size']
        )
        
        # Create a new browser instance
        browser = Browser(
            config=BrowserConfig(
                headless=False,  # Fresh instance for Fieldd
                disable_images=True,  # Disable image loading
                disable_javascript=False,  # Keep JavaScript enabled for form interactions
                disable_css=False  # Keep CSS enabled for proper UI rendering
            )
        )
        
        # Create a new agent with the formatted message
        agent = Agent(
            task="Create a new quote in Fieldd CRM using the extracted GHL data",
            llm=ChatOpenAI(model='gpt-4o'),
            browser=browser,
            extend_system_message=formatted_message
        )
        
        # Run the agent
        print("\n=== Starting Fieldd Quote Creation ===", file=sys.stderr)
        result = await agent.run()
        print("=== Automation Complete ===\n", file=sys.stderr)
        
        # Close the browser
        await browser.close()
        return result
        
    except Exception as e:
        print(f"Error in automation: {str(e)}", file=sys.stderr)
        return None

def check_webhook_data():
    """Check for new webhook data from Railway"""
    try:
        print("\nChecking for new webhook data...", file=sys.stderr)
        # Get the latest webhook data from Railway
        response = requests.get('https://ghlwebhook-production.up.railway.app/latest_webhook')
        print(f"Response status code: {response.status_code}", file=sys.stderr)
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response data: {json.dumps(response_data, indent=2)}", file=sys.stderr)
            
            if response_data.get('data_received'):
                print("New data received! Starting automation...", file=sys.stderr)
                # Pass the nested data to run_automation
                asyncio.run(run_automation(response_data['data']))
            else:
                print("No new data received", file=sys.stderr)
        else:
            print(f"Error: Received status code {response.status_code}", file=sys.stderr)
            
    except Exception as e:
        print(f"Error checking webhook: {str(e)}", file=sys.stderr)

def main():
    print("\n=== Starting Local Automation Listener ===", file=sys.stderr)
    
    # Clear any existing webhook data when starting up
    clear_webhook_data()
    
    print("Checking for webhook data every 5 seconds...", file=sys.stderr)
    print("Press Ctrl+C to stop", file=sys.stderr)
    print("=======================================\n", file=sys.stderr)
    
    while True:
        check_webhook_data()
        time.sleep(5)  # Check every 5 seconds

if __name__ == '__main__':
    main() 