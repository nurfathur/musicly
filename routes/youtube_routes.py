from flask import Blueprint, request
import logging
import asyncio
from controllers.youtube_controller import YouTubeController

logger = logging.getLogger(__name__)

# Create blueprint
youtube_bp = Blueprint('youtube', __name__)

# Initialize controller
youtube_controller = YouTubeController()

@youtube_bp.route('/search', methods=['GET'])
def search_youtube():
    """
    Route to search YouTube videos
    
    Query parameters:
    - q: Search query (required)
    - limit: Maximum number of results (default: 20)
    - minDuration: Minimum duration in seconds (default: 0)
    - maxDuration: Maximum duration in seconds (default: 600)
    - filterLive: Whether to filter live videos (default: true)
    - includeMetadata: Whether to include additional metadata (default: true)
    
    Response:
    {
        "success": true,
        "data": {
            "query": "search query",
            "totalResults": 10,
            "results": [...]
        }
    }
    """
    try:
        # Get search query
        query = request.args.get('q')
        
        # Extract configuration options from query parameters
        options = {
            'limit': int(request.args.get('limit', 20)),
            'min_duration': int(request.args.get('minDuration', 0)),
            'max_duration': int(request.args.get('maxDuration', 600)),
            'filter_live': request.args.get('filterLive', 'true').lower() != 'false',
            'include_metadata': request.args.get('includeMetadata', 'true').lower() != 'false'
        }
        
        # Execute search asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(youtube_controller.search(query, options))
        loop.close()
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search route: {str(e)}")
        from utils.response import error_response
        return error_response(f"Server error: {str(e)}", 500)

@youtube_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    Route to clear search cache
    
    Response:
    {
        "success": true,
        "data": {
            "success": true,
            "message": "Cache cleared"
        }
    }
    """
    return youtube_controller.clear_cache()

@youtube_bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """
    Route to get cache statistics
    
    Response:
    {
        "success": true,
        "data": {
            "cache": {
                "size": 10,
                "max_size": 100,
                "ttl_seconds": 3600
            }
        }
    }
    """
    return youtube_controller.get_cache_statistics()