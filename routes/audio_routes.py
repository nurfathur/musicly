from flask import Blueprint, request
import logging
from controllers.audio_controller import AudioController
from utils.response import error_response

logger = logging.getLogger(__name__)

# Create blueprint
audio_bp = Blueprint('audio', __name__)

# Initialize controller
audio_controller = AudioController()

@audio_bp.route('/download', methods=['POST'])
def download_audio():
    try:
        # Get request data
        data = request.get_json()
        
        # Validate request data
        if not data:
            return error_response("Invalid JSON data", 400)
            
        video_url = data.get('url')
        if not video_url:
            return error_response("No URL provided", 400)
        
        # Process the request
        return audio_controller.process_audio(video_url)
        
    except Exception as e:
        logger.error(f"Error in download route: {str(e)}")
        return error_response("Server error", 500)

