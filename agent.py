from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

import asyncio
import os

# Load environment variables
FIELDD_USERNAME = os.getenv('FIELDD_USERNAME')
FIELDD_PASSWORD = os.getenv('FIELDD_PASSWORD')
COMPANY_CITY = os.getenv('COMPANY_CITY')

# GHL system message for data extraction
ghl_extend_system_message = """
When extracting data from GHL conversation:
1. IMPORTANT: DO NOT navigate to any URL. Use ONLY the current tab that's already open:
   - The browser is already connected to your current Chrome session
   - Use ONLY the current tab that's open to GHL
   - DO NOT open new tabs or navigate to new URLs
   - If you don't see the GHL conversation in the current tab, stop and report an error
   - The current URL should contain 'fluxconsulting.co' and 'conversations'

2. In the current GHL conversation window:
   - Find and extract customer name using:
     * Look for "Name:" or "Customer:" labels
     * Find the text following these labels
   - Find and extract email using:
     * Look for "Email:" label
     * Find the text following this label
   - Find and extract phone using:
     * Look for "Phone:" or "Tel:" labels
     * Find the text following these labels
   - Find and extract address using:
     * Look for "Address:" label
     * Find the text following this label
   - Find and extract service request using:
     * Look for "Service:" or "Request:" labels
     * Find the text following these labels

3. Save all extracted data in this format:
   customer_name = [extracted name]
   customer_email = [extracted email]
   customer_phone = [extracted phone]
   customer_address = [extracted address]
   service_request = [extracted service]
"""

# Update Fieldd system message to use GHL data
extend_system_message = f"""
When creating a quote in Fieldd CRM:
1. Navigate to https://admin.fieldd.co/#!/company/schedule/planner
2. Log into fieldd: 
   - Enter email using the "email" login field:
   - Username: {FIELDD_USERNAME}
   - Hit the "next" arrow button to open the password field
   - Enter password using the "password" login field:
   - Password: {FIELDD_PASSWORD}
   - Login
3. Once logged in, hit "new" and then select "quote"
4. Find the "Customer" section and enter the following:
    first name: [customer_name.split()[0]]  # First part of the name
    last name: [customer_name.split()[-1]]  # Last part of the name
    Address field instructions:
    - Find input field with ng-model="formData.customerAddress"
    - Type "[customer_address]" and wait for dropdown
    - Look for dropdown items with class="ui-select-choices-row"
    - Select the item that contains "{COMPANY_CITY}"
    - If dropdown doesn't appear, try clicking the field first
    - If still no dropdown, try typing the address slowly
    Email (with ng-model="formData.customerEmail"): [customer_email]
    Phone (with ng-model="viewData.customerPhone"): [customer_phone]
5. Job Address field instructions:
    - Find input field with ng-model="formData.jobAddress"
    - Enter: [customer_address]
    - Wait for dropdown
    - Look for dropdown items with class="ui-select-choices-row"
    - Select the item that contains "{COMPANY_CITY}"
    - If dropdown doesn't appear, try clicking the field first
    - If still no dropdown, try typing the address slowly
6. Under "acceptance" select "self schedule"
7. In input field with ng-model="item.name", first type "[service_request]" in the search bar, then select coupe option
8. Select "send quote"
9. If quote fails, look for the error message and follow the instructions to fix the error
"""

# Configure browsers
ghl_browser = Browser(
    config=BrowserConfig(
        connect_to_existing=True,
        # Prevent new tabs and windows
        chrome_flags=[
            '--disable-popup-blocking',
            '--disable-new-window',
            '--disable-tab-creation'
        ]
    )
)

fieldd_browser = Browser(
    config=BrowserConfig(
        headless=False  # Fresh instance for Fieldd
    )
)

# Create both agents
ghl_agent = Agent(
    task="Extract customer data from the CURRENT tab ONLY - DO NOT navigate or open new tabs",
    llm=ChatOpenAI(model='gpt-4o'),
    browser=ghl_browser,
    extend_system_message=ghl_extend_system_message
)

fieldd_agent = Agent(
    task="Create a new quote in Fieldd CRM using the extracted GHL data",
    llm=ChatOpenAI(model='gpt-4o-mini'),
    browser=fieldd_browser,
    extend_system_message=extend_system_message
)

async def main():
    # First run GHL agent
    print("\n=== Extracting data from GHL ===")
    ghl_result = await ghl_agent.run()
    
    # Print all extracted data in a clear format
    print("\n=== Extracted GHL Data ===")
    print("Customer Name:", ghl_result.get('customer_name', 'Not found'))
    print("Customer Email:", ghl_result.get('customer_email', 'Not found'))
    print("Customer Phone:", ghl_result.get('customer_phone', 'Not found'))
    print("Customer Address:", ghl_result.get('customer_address', 'Not found'))
    print("Service Request:", ghl_result.get('service_request', 'Not found'))
    
    # Ask for confirmation before proceeding
    input("\nPress Enter to proceed with quote creation using this data...")
    
    # Update Fieldd agent with GHL data
    fieldd_agent = Agent(
        task="Create a new quote in Fieldd CRM using the extracted GHL data",
        llm=ChatOpenAI(model='gpt-4o-mini'),
        browser=fieldd_browser,
        extend_system_message=extend_system_message.format(
            customer_name=ghl_result.get('customer_name', ''),
            customer_email=ghl_result.get('customer_email', ''),
            customer_phone=ghl_result.get('customer_phone', ''),
            customer_address=ghl_result.get('customer_address', ''),
            service_request=ghl_result.get('service_request', '')
        )
    )
    
    # Then run Fieldd agent
    print("\n=== Creating Fieldd quote ===")
    fieldd_result = await fieldd_agent.run()
    print("Fieldd Result:", fieldd_result)
    
    input('Press Enter to close the browsers...')
    await ghl_browser.close()
    await fieldd_browser.close()

if __name__ == '__main__':
    asyncio.run(main())