import yt_dlp
import logging

logger = logging.getLogger(__name__)

class AudioDownloader:
    """Service for downloading audio from video URLs"""

    def __init__(self, quality='192', cookies_path=None):
        """
        Args:
            quality (str): Audio quality in kbps
            cookies_path (str): Path to cookies.txt file (optional)
        """
        self.quality = quality
        self.cookies_path = cookies_path

    def download_audio(self, url, output_filename):
        """Download audio from URL and convert to MP3"""
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

            if self.cookies_path:
                ydl_opts['cookiefile'] = self.cookies_path

            logger.info(f"Downloading audio from {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            final_filename = f"{output_filename}.mp3"
            logger.info(f"Download complete: {final_filename}")
            return final_filename

        except Exception as e:
            logger.error(f"Download failed: {str(e)}")
            raise Exception(f"Failed to download audio: {str(e)}")
