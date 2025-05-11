import os
import uuid
import logging
import yt_dlp
import tempfile
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioDownloader:
    """Service for downloading audio from video URLs"""
    
    def __init__(self, quality='192', ffmpeg_path=None):
        """
        Args:
            quality (str): Audio quality in kbps
            ffmpeg_path (str): Path to ffmpeg binary (optional)
        """
        self.quality = quality
        self.ffmpeg_path = ffmpeg_path
        
    def _generate_temp_cookies_file(self):
        """Create a temporary cookies file from environment variables"""
        try:
            # Check if cookies are provided in environment variable
            cookies_env = os.getenv('YOUTUBE_COOKIES')
            
            if not cookies_env:
                logger.warning("No YOUTUBE_COOKIES environment variable found.")
                return None
                
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix='.txt')
            logger.info(f"Created temporary cookies file at {temp_path}")
            
            # Write cookies to temporary file
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(cookies_env)
                
            # Make sure file has correct permissions
            os.chmod(temp_path, 0o644)
            
            return temp_path
        except Exception as e:
            logger.error(f"Failed to create temporary cookies file: {e}")
            return None

    def download_audio(self, url, output_filename):
        """Download audio from URL and convert to MP3"""
        temp_cookies = None
        
        try:
            logger.info(f"Preparing to download audio from {url}")
            
            # Create directory for output if it doesn't exist
            output_dir = os.path.dirname(output_filename)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
            
            ydl_opts = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                'http_headers': {
                    'referer': 'https://www.youtube.com/',
                    'origin': 'https://www.youtube.com'
                },
                'format': 'bestaudio/best',
                'outtmpl': output_filename,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                }],
                'quiet': False,
                'verbose': True
            }

            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path

            # Try to use cookies from environment
            temp_cookies = self._generate_temp_cookies_file()
            if temp_cookies:
                logger.info(f"Using temporary cookies file: {temp_cookies}")
                ydl_opts['cookiefile'] = temp_cookies
            
            # Authentication methods in order of preference
            logger.info("Starting download attempt with provided authentication")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            final_filename = f"{output_filename}.mp3"
            
            if os.path.exists(final_filename):
                file_size = os.path.getsize(final_filename) / (1024 * 1024)  # Size in MB
                logger.info(f"Download complete: {final_filename} ({file_size:.2f} MB)")
                return final_filename
            else:
                raise Exception(f"Output file not found after download: {final_filename}")

        except Exception as e:
            logger.error(f"Download failed with provided authentication: {str(e)}")
            
            # If authentication failed, try fallback methods
            try:
                logger.info("Trying fallback: public video access")
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_filename,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': self.quality,
                    }],
                    'quiet': False
                }
                
                if self.ffmpeg_path:
                    ydl_opts['ffmpeg_location'] = self.ffmpeg_path
                    
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
                final_filename = f"{output_filename}.mp3"
                if os.path.exists(final_filename):
                    return final_filename
                    
            except Exception as fallback_error:
                logger.error(f"Fallback download also failed: {str(fallback_error)}")
                raise Exception(f"All download attempts failed: {str(e)}")
                
        finally:
            # Clean up temp file
            if temp_cookies and os.path.exists(temp_cookies):
                try:
                    os.remove(temp_cookies)
                    logger.info(f"Removed temporary cookies file: {temp_cookies}")
                except Exception as cleanup_error:
                    logger.warning(f"Failed to remove temporary cookies file: {cleanup_error}")

