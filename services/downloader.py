import yt_dlp
import logging

logger = logging.getLogger(__name__)

class AudioDownloader:
    """Service for downloading audio from video URLs"""
    
    def __init__(self, quality='192'):
        """Initialize the downloader with default settings
        
        Args:
            quality (str): Audio quality in kbps
        """
        self.quality = quality
        
    def download_audio(self, url, output_filename):
        """Download audio from URL and convert to MP3
        
        Args:
            url (str): URL of the video to download
            output_filename (str): Output filename for the downloaded audio
            
        Returns:
            str: Path to the downloaded audio file
            
        Raises:
            Exception: If download fails
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_filename,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                }],
                'quiet': True
            }
            
            logger.info(f"Downloading audio from {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            # yt-dlp adds extension after processing
            final_filename = f"{output_filename}.mp3"
            logger.info(f"Download complete: {final_filename}")
            return final_filename
            
        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            raise Exception(f"Failed to download audio: {str(e)}")