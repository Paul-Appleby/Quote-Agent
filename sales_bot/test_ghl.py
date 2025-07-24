import asyncio
from ghl_api import GHLAPI
import logging
from config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ghl_sms():
    ghl = GHLAPI()
    
    # Get the test contact ID from settings
    if not settings.ALLOWED_CONTACT_IDS:
        logger.error("No test contact IDs configured in settings.ALLOWED_CONTACT_IDS")
        return
    
    contact_id = settings.ALLOWED_CONTACT_IDS[0]
    logger.info(f"Using test contact ID: {contact_id}")
    
    # Test message
    message = "This is a test message from the sales bot! Please respond with 'Hi' to start a conversation."
    
    # Send the message
    logger.info(f"Sending test message to contact {contact_id}")
    success = await ghl.send_sms(contact_id, message)
    
    if success:
        logger.info("Test message sent successfully!")
    else:
        logger.error("Failed to send test message")

if __name__ == "__main__":
    logger.info("Starting GHL SMS test...")
    asyncio.run(test_ghl_sms()) 