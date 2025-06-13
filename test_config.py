import asyncio
import logging
from services.config_system import ConfigSystem
from services.token_systems import TokenSystem
from services.auth_system import AuthSystem
from services.ghl_service import GHLService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_configuration():
    try:
        # Initialize systems
        logger.info("Initializing systems...")
        config_system = ConfigSystem()
        token_system = TokenSystem()
        auth_system = AuthSystem(config_system, token_system)
        
        # Test token generation
        logger.info("Testing token generation...")
        token = await token_system.get_valid_token()
        logger.info("Successfully generated token!")
        
        # Test API connection
        logger.info("Testing API connection...")
        ghl_service = GHLService(auth_system)
        response = await ghl_service.make_authenticated_request(
            "GET",
            "/locations/current"
        )
        logger.info(f"Successfully connected to API! Location: {response.get('name')}")
        
        logger.info("All tests passed! Configuration is valid.")
        
    except Exception as e:
        logger.error(f"Configuration test failed: {str(e)}")
        raise
    finally:
        if 'auth_system' in locals():
            await auth_system.revoke_token()

if __name__ == "__main__":
    asyncio.run(test_configuration())