import yt_dlp
import logging

logger = logging.getLogger(__name__)

class AudioDownloader:
    """Service for downloading audio from video URLs"""

    def __init__(self, quality='192', ffmpeg_path=None, cookies_path=None):
        """
        Args:
            quality (str): Audio quality in kbps
            ffmpeg_path (str): Path to ffmpeg binary (optional)
            cookies_path (str): Path to cookies.txt file (optional)
        """
        self.quality = quality
        self.ffmpeg_path = ffmpeg_path
        self.cookies_path = cookies_path

    def download_audio(self, url, output_filename):
        """Download audio from URL and convert to MP3"""
        try:
            ydl_opts = {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                'http_headers': {
                    'referer': 'https://www.youtube.com/'
                },
                'format': 'bestaudio/best',
                'outtmpl': output_filename,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                }],
                'quiet': True
            }

            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path

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
