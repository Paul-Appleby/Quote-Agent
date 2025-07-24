import aiohttp
import sqlite3
from typing import Dict, Any
from config import Settings

settings = Settings()

async def get_customer_data(data: dict) -> Dict[str, Any]:
    """Extract and validate customer data from GHL webhook"""
    try:
        contact = data.get("contact", {})
        return {
            "id": contact.get("id"),
            "name": contact.get("name"),
            "phone": contact.get("phone"),
            "email": contact.get("email"),
            "address": contact.get("address"),
            "custom_fields": contact.get("customFields", {})
        }
    except Exception as e:
        raise Exception(f"Error extracting customer data: {str(e)}")

async def get_sop_data(customer_data: dict) -> Dict[str, Any]:
    """Get relevant SOP data from database"""
    try:
        conn = sqlite3.connect("db/sops.db")
        cursor = conn.cursor()
        
        # Get SOP based on customer state and preferences
        cursor.execute("""
            SELECT * FROM sops 
            WHERE state = ? AND service_type = ?
        """, (customer_data.get("state"), customer_data.get("service_type")))
        
        sop = cursor.fetchone()
        conn.close()
        
        if not sop:
            return {"next_steps": ["Follow up with customer"]}
            
        return {
            "next_steps": sop.get("next_steps", []),
            "templates": sop.get("templates", {}),
            "rules": sop.get("rules", {})
        }
    except Exception as e:
        raise Exception(f"Error getting SOP data: {str(e)}")

async def create_fieldd_quote(customer_data: dict, sop_data: dict) -> Dict[str, Any]:
    """Create quote in Fieldd CRM"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.FIELDD_API_URL}/quotes",
                json={
                    "customer": customer_data,
                    "sop": sop_data
                },
                headers={"Authorization": f"Bearer {settings.FIELDD_API_KEY}"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Fieldd API error: {await response.text()}")
                return await response.json()
    except Exception as e:
        raise Exception(f"Error creating Fieldd quote: {str(e)}")

async def send_sms_response(phone: str, message: str) -> None:
    """Send SMS response via GHL API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.GHL_API_URL}/messages",
                json={
                    "phone": phone,
                    "message": message
                },
                headers={"Authorization": f"Bearer {settings.GHL_API_KEY}"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"GHL API error: {await response.text()}")
    except Exception as e:
        raise Exception(f"Error sending SMS: {str(e)}")

async def update_lead_status(lead_id: str, response: str) -> None:
    """Update lead status in GHL"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{settings.GHL_API_URL}/contacts/{lead_id}",
                json={
                    "status": "responded",
                    "lastResponse": response
                },
                headers={"Authorization": f"Bearer {settings.GHL_API_KEY}"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"GHL API error: {await response.text()}")
    except Exception as e:
        raise Exception(f"Error updating lead status: {str(e)}") 