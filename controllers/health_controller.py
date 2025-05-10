import os
import logging
import cloudinary
import cloudinary.api

from utils.response import success_response

logger = logging.getLogger(__name__)

class HealthController:
    """Controller for health check operations"""
    
    def __init__(self):
        """Initialize the health controller"""
        self.version = "1.0.0"
    
    def check_health(self):
        """
        Perform health checks on system and dependencies
        
        Returns:
            Response: Flask response object with health status
        """
        try:
            # Check Cloudinary connection
            cloudinary_status = "unknown"
            try:
                # Simple check to see if Cloudinary credentials are valid
                if (os.getenv('CLOUD_NAME') and 
                    os.getenv('API_KEY') and 
                    os.getenv('API_SECRET')):
                    # This will fail if credentials are invalid
                    cloudinary.api.ping()
                    cloudinary_status = "ok"
                else:
                    cloudinary_status = "not configured"
            except Exception as e:
                logger.warning(f"Cloudinary health check failed: {str(e)}")
                cloudinary_status = "error"
            
            # Compile health data
            health_data = {
                "status": "ok",
                "version": self.version,
                "services": {
                    "cloudinary": cloudinary_status
                }
            }
            
            return success_response(health_data)
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            # Even on error, we return 200 but with error status
            return success_response({
                "status": "error",
                "error": str(e),
                "version": self.version
            })