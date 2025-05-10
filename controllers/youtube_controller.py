import logging
import asyncio
from typing import Dict, Any

from services.youtube import search_videos, clear_search_cache, get_cache_stats
from utils.response import success_response, error_response

logger = logging.getLogger(__name__)

class YouTubeController:
    """Controller for YouTube search operations"""
    
    def __init__(self):
        """Initialize YouTube controller"""
        pass
    
    async def search(self, query: str, options: Dict[str, Any] = None) -> tuple:
        """
        Search for YouTube videos
        
        Args:
            query (str): Search query
            options (Dict[str, Any], optional): Search options
            
        Returns:
            tuple: Flask response object (JSON response, status code)
        """
        try:
            if not query:
                return error_response("Missing search query", 400)
                
            logger.info(f"Processing search request for: {query}")
            
            # Execute search
            results = await search_videos(query, options)
            
            # Check if search was successful
            if not results.get('success', False):
                error_msg = results.get('error', 'Unknown search error')
                logger.warning(f"Search failed: {error_msg}")
                return error_response(error_msg, 500)
                
            logger.info(f"Search successful, found {results.get('totalResults', 0)} results")
            return success_response(results)
            
        except ValueError as e:
            logger.warning(f"Invalid search parameters: {str(e)}")
            return error_response(str(e), 400)
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return error_response(f"An error occurred during search: {str(e)}", 500)
    
    def clear_cache(self) -> tuple:
        """
        Clear search cache
        
        Returns:
            tuple: Flask response object (JSON response, status code)
        """
        try:
            result = clear_search_cache()
            logger.info("Search cache cleared")
            return success_response(result)
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return error_response(f"Failed to clear cache: {str(e)}", 500)
    
    def get_cache_statistics(self) -> tuple:
        """
        Get cache statistics
        
        Returns:
            tuple: Flask response object (JSON response, status code)
        """
        try:
            stats = get_cache_stats()
            logger.info(f"Retrieved cache stats: {stats}")
            return success_response({"cache": stats})
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return error_response(f"Failed to get cache stats: {str(e)}", 500)