from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import asyncio
from agent import fieldd_agent, fieldd_browser

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Log the received data
            print("\n=== Received Webhook Data ===")
            print("Timestamp:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print("Contact Info:", json.dumps(data.get('contact', {}), indent=2))
            print("Conversation Info:", json.dumps(data.get('conversation', {}), indent=2))
            print("Custom Variables:", json.dumps(data.get('customVariables', {}), indent=2))
            
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
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'success',
                'message': 'Quote created successfully'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            # Log the error
            print(f"\n=== Error Processing Webhook ===")
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Error: {str(e)}")
            print("===========================\n")
            
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(response).encode()) 