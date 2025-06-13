from typing import Optional, Dict, Any, List
import logging
from .auth_system import AuthSystem

logger = logging.getLogger(__name__)

class GHLService:
    """Service for interacting with GoHighLevel API"""
    
    def __init__(self, auth_system: AuthSystem):
        self.auth = auth_system
        logger.info("GHLService initialized")
    
    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Any:
        """Make an authenticated API request"""
        return await self.auth.make_authenticated_request(
            method=method,
            endpoint=endpoint,
            data=data,
            params=params
        )
    
    async def get_new_messages(self) -> List[Dict]:
        """Get new messages from GHL"""
        try:
            response = await self.make_authenticated_request(
                method="GET",
                endpoint="/conversations/messages",
                params={"status": "unread"}
            )
            return response.get("messages", [])
        except Exception as e:
            logger.error(f"Failed to get new messages: {str(e)}")
            return []
    
    async def get_contact(self, contact_id: str) -> Dict:
        """Get contact details"""
        try:
            response = await self.make_authenticated_request(
                method="GET",
                endpoint=f"/contacts/{contact_id}"
            )
            return response
        except Exception as e:
            logger.error(f"Failed to get contact {contact_id}: {str(e)}")
            raise
    
    async def create_contact(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        email: Optional[str] = None
    ) -> Dict:
        """Create a new contact"""
        data = {
            "firstName": first_name,
            "lastName": last_name,
            "phone": phone,
            "email": email
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint="/contacts",
                data=data
            )
            logger.info(f"Created contact for {first_name} {last_name}")
            return response
        except Exception as e:
            logger.error(f"Failed to create contact: {str(e)}")
            raise
    
    async def search_contacts(self, query: str) -> List[Dict]:
        """Search for contacts"""
        try:
            response = await self.make_authenticated_request(
                method="GET",
                endpoint="/contacts/search",
                params={"query": query}
            )
            return response.get("contacts", [])
        except Exception as e:
            logger.error(f"Failed to search contacts: {str(e)}")
            raise
    
    async def send_sms(
        self,
        contact_id: str,
        message: str,
        location_id: Optional[str] = None
    ) -> Dict:
        """Send SMS to a contact"""
        endpoint = f"/locations/{location_id}/conversations/messages" if location_id else "/conversations/messages"
        
        data = {
            "contactId": contact_id,
            "body": message,
            "channelType": "sms"
        }
        
        try:
            response = await self.make_authenticated_request(
                method="POST",
                endpoint=endpoint,
                data=data
            )
            logger.info(f"SMS sent to contact {contact_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to send SMS to contact {contact_id}: {str(e)}")
            raise 