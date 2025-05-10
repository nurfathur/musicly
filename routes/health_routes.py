from flask import Blueprint
from controllers.health_controller import HealthController

# Create blueprint
health_bp = Blueprint('health', __name__)

# Initialize controller
health_controller = HealthController()

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify the API is operational
    
    Response:
    {
        "success": true,
        "data": {
            "status": "ok",
            "version": "1.0.0",
            "services": {
                "cloudinary": "ok"
            }
        }
    }
    """
    return health_controller.check_health()