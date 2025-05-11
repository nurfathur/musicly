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
        # Use environment variable for ffmpeg path
        ffmpeg_path = os.getenv('FFMPEG_PATH', '/usr/bin/ffmpeg')
        
        self.downloader = AudioDownloader(
            ffmpeg_path=ffmpeg_path
        )
        
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
            dict: Response dictionary
        """
        try:
            # Generate unique filename
            unique_id = str(uuid.uuid4())
            output_dir = os.getenv('TEMP_DIR', '/tmp')
            output_filename = os.path.join(output_dir, unique_id)
            
            logger.info(f"Starting audio processing for URL: {video_url}")
            
            # Download audio (returns full .mp3 path)
            downloaded_file = self.downloader.download_audio(
                video_url,
                output_filename
            )
            
            # Upload to Cloudinary
            uploaded_url = self.uploader.upload_file(downloaded_file)
            
            # Clean up
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
                logger.info(f"Removed temporary file: {downloaded_file}")
            
            return {"success": True, "url": uploaded_url}
        
        except Exception as e:
            logger.error(f"Audio processing error: {str(e)}")
            return {"success": False, "error": str(e)}
