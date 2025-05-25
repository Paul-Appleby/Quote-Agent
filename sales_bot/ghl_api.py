import os
import httpx
from dotenv import load_dotenv
from typing import Optional
import aiohttp
import logging
from config import settings

# Load environment variables
load_dotenv()

# GHL API Configuration
GHL_API_KEY = os.getenv("GHL_API_KEY")
GHL_API_URL = "https://rest.gohighlevel.com/v1"

logger = logging.getLogger(__name__)

class GHLAPI:
    def __init__(self):
        self.api_key = settings.GHL_API_KEY
        self.base_url = settings.GHL_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_sms(self, contact_id: str, message: str) -> bool:
        """
        Send an SMS message to a contact via GHL.
        
        Args:
            contact_id: The GHL contact ID
            message: The message to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/contacts/{contact_id}/sms"
            payload = {
                "message": message
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent SMS to contact {contact_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send SMS to contact {contact_id}. Status: {response.status}, Error: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error sending SMS to contact {contact_id}: {str(e)}")
            return False
    
    async def get_contact(self, contact_id: str) -> dict:
        """
        Get contact information from GHL.
        
        Args:
            contact_id: The GHL contact ID
            
        Returns:
            dict: Contact information or empty dict if failed
        """
        try:
            url = f"{self.base_url}/contacts/{contact_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get contact {contact_id}. Status: {response.status}, Error: {error_text}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Error getting contact {contact_id}: {str(e)}")
            return {}
    
    async def update_contact(self, contact_id: str, data: dict) -> bool:
        """
        Update contact information in GHL.
        
        Args:
            contact_id: The GHL contact ID
            data: The data to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/contacts/{contact_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, json=data, headers=self.headers) as response:
                    if response.status == 200:
                        logger.info(f"Successfully updated contact {contact_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to update contact {contact_id}. Status: {response.status}, Error: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error updating contact {contact_id}: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_sms():
        ghl = GHLAPI()
        # Replace with a real contact ID for testing
        contact_id = "test_contact_id"
        success = await ghl.send_sms(
            contact_id=contact_id,
            message="This is a test message from the sales bot!"
        )
        print(f"SMS sent successfully: {success}")
    
    asyncio.run(test_sms()) 