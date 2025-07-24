from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import json
import logging
from config import get_settings
from sales_agent import SalesAgent
from db.db_utils import DatabaseManager
from ghl_api import GHLAPI

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()
settings = get_settings()
db = DatabaseManager()
agent = SalesAgent()
ghl = GHLAPI()

class SMSMessage(BaseModel):
    id: str
    contact_id: str
    message: str
    direction: str
    status: str
    created_at: str
    pipeline_name: str = ""

def should_process_message(contact_id: str, pipeline_name: str) -> bool:
    """
    Determine if we should process this message based on configuration.
    
    Args:
        contact_id: The GHL contact ID
        pipeline_name: The contact's current pipeline name
        
    Returns:
        bool: True if we should process this message
    """
    # Check if we're restricting to specific contacts
    if settings.RESTRICT_TO_SPECIFIC_CONTACTS:
        if contact_id not in settings.ALLOWED_CONTACT_IDS:
            logger.info(f"Skipping message from contact {contact_id} - not in allowed contacts list")
            return False
    
    # Check if the pipeline name is allowed
    if pipeline_name not in settings.ALLOWED_PIPELINE_STAGES:
        logger.info(f"Skipping message from contact {contact_id} - pipeline '{pipeline_name}' not allowed")
        return False
    
    return True

@app.post("/webhook")
async def webhook(request: Request):
    """Handle incoming webhooks from GHL"""
    try:
        # Get the raw webhook data
        data = await request.json()
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        # If it's an SMS event, process it
        if data.get("event") == "sms.received":
            sms_data = SMSMessage(**data.get("data", {}))
            
            # Get pipeline name from contact data
            pipeline_name = data.get("data", {}).get("pipeline", {}).get("name", "")
            
            # Check if we should process this message
            if should_process_message(sms_data.contact_id, pipeline_name):
                logger.info(f"Processing SMS from {sms_data.contact_id} in pipeline '{pipeline_name}': {sms_data.message}")
                
                # Store the incoming message
                db.store_message(
                    contact_id=sms_data.contact_id,
                    message=sms_data.message,
                    sender='customer'
                )
                
                # Get conversation history for context
                history = db.get_conversation_history(sms_data.contact_id)
                
                # Generate response using the sales agent
                response = agent.generate_response(sms_data.message, history)
                
                # Store the agent's response
                db.store_message(
                    contact_id=sms_data.contact_id,
                    message=response,
                    sender='agent'
                )
                
                # Send response back to GHL
                success = await ghl.send_sms(sms_data.contact_id, response)
                
                if not success:
                    raise HTTPException(status_code=500, detail="Failed to send SMS response")
                
                return {"status": "success", "message": "SMS processed"}
            else:
                logger.info(f"Skipping SMS from {sms_data.contact_id}")
        
        return {"status": "success", "message": "Webhook received"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return "pong"

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting webhook server...")
    logger.info(f"Allowed pipelines: {settings.ALLOWED_PIPELINE_STAGES}")
    logger.info(f"Restricted to specific contacts: {settings.RESTRICT_TO_SPECIFIC_CONTACTS}")
    if settings.RESTRICT_TO_SPECIFIC_CONTACTS:
        logger.info(f"Allowed contact IDs: {settings.ALLOWED_CONTACT_IDS}")
    uvicorn.run(app, host="0.0.0.0", port=8000) 