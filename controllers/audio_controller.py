import os
import uuid
import logging
from services.downloader import AudioDownloader
from services.uploader import CloudinaryUploader
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

class AudioController:
    """Controller for audio processing operations"""
    
    def __init__(self):
        """Initialize the audio controller with required services"""
        self.downloader = AudioDownloader()
        self.uploader = CloudinaryUploader(
            cloud_name=os.getenv('CLOUD_NAME'),
            api_key=os.getenv('API_KEY'),
            api_secret=os.getenv('API_SECRET')
        )
    
    def process_audio(self, video_url):
        """
        Process an audio download and upload request
        
        Args:
            video_url (str): URL of the video to process
            
        Returns:
            Response: Flask response object
        """
        try:
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            output_filename = f"{unique_id}"
            
            # Download audio
            logger.info(f"Starting audio processing for URL: {video_url}")
            downloaded_file = AudioDownloader(video_url, output_filename,cookies_path='./data/cookies.txt')
            
            
            # Upload to cloud storage
            uploaded_url = self.uploader.upload_file(downloaded_file)
            
            # Clean up temporary file
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
                logger.info(f"Removed temporary file: {downloaded_file}")
            
            return success_response({"url": uploaded_url})
            
        except Exception as e:
            logger.error(f"Audio processing error: {str(e)}")
            return error_response(f"Processing error: {str(e)}", 500)