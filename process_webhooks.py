import os
import json
import asyncio
from agent import fieldd_agent
from datetime import datetime

WEBHOOK_DATA_DIR = 'webhook_data'

def process_webhook_file(filename):
    """Process a single webhook data file"""
    try:
        # Read webhook data
        with open(filename, 'r') as f:
            data = json.load(f)
        
        print(f"\n=== Processing Webhook Data: {filename} ===")
        print("Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Extract contact info
        contact_info = data.get('contact', {})
        customer_data = {
            'name': contact_info.get('name', ''),
            'email': contact_info.get('email', ''),
            'phone': contact_info.get('phone', ''),
            'address': contact_info.get('address', ''),
            'service_request': contact_info.get('service_request', '')
        }
        
        # Update Fieldd agent with customer data
        fieldd_agent.extend_system_message = fieldd_agent.extend_system_message.format(
            customer_name=customer_data['name'],
            customer_email=customer_data['email'],
            customer_phone=customer_data['phone'],
            customer_address=customer_data['address'],
            service_request=customer_data['service_request']
        )
        
        # Create the quote
        asyncio.run(fieldd_agent.run())
        
        # Move processed file to a 'processed' subdirectory
        processed_dir = os.path.join(WEBHOOK_DATA_DIR, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        os.rename(filename, os.path.join(processed_dir, os.path.basename(filename)))
        
        print("Quote created successfully!")
        print("===========================\n")
        
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

def main():
    # Get list of webhook data files
    webhook_files = [f for f in os.listdir(WEBHOOK_DATA_DIR) 
                    if f.startswith('webhook_') and f.endswith('.json')]
    
    if not webhook_files:
        print("No webhook data files to process")
        return
    
    # Process each file
    for filename in sorted(webhook_files):
        full_path = os.path.join(WEBHOOK_DATA_DIR, filename)
        process_webhook_file(full_path)

if __name__ == '__main__':
    main() 