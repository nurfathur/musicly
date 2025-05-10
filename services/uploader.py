import cloudinary
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)

class CloudinaryUploader:
    """Service for uploading files to Cloudinary"""
    
    def __init__(self, cloud_name=None, api_key=None, api_secret=None):
        """Initialize Cloudinary configuration
        
        Args:
            cloud_name (str): Cloudinary cloud name
            api_key (str): Cloudinary API key
            api_secret (str): Cloudinary API secret
        """
        # Configure Cloudinary
        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
        else:
            logger.warning("Cloudinary credentials not fully provided")
            
    def upload_file(self, file_path):
        """Upload a file to Cloudinary
        
        Args:
            file_path (str): Path to the file to upload
            
        Returns:
            str: Public URL of the uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            logger.info(f"Uploading file to Cloudinary: {file_path}")
            response = cloudinary.uploader.upload(file_path, resource_type="video")
            
            if 'secure_url' in response:
                logger.info(f"Upload successful: {response['secure_url']}")
                return response['secure_url']
            else:
                logger.error("Upload response missing secure_url")
                raise Exception("Invalid upload response from Cloudinary")
                
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")