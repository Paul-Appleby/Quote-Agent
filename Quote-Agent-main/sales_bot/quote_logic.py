from data_utils import get_customer_data, get_sop_data, create_fieldd_quote
from config import Settings

settings = Settings()

async def handle_quote_request(data: dict) -> dict:
    """
    Handle quote requests from GHL
    Returns quote details and next steps
    """
    try:
        # Extract customer data from GHL
        customer_data = await get_customer_data(data)
        
        # Get relevant SOP data
        sop_data = await get_sop_data(customer_data)
        
        # Create quote in Fieldd
        quote_result = await create_fieldd_quote(customer_data, sop_data)
        
        return {
            "status": "success",
            "quote_id": quote_result.get("quote_id"),
            "next_steps": sop_data.get("next_steps", []),
            "message": "Quote created successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        } 