import re
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

# Import youtube search libraries
from youtubesearchpython import VideosSearch

# Configure logging
logger = logging.getLogger(__name__)

# Pre-compile regex pattern
MUSIC_REGEX = re.compile(r'music', re.IGNORECASE)

# Cache configuration
class SearchCache:
    """Simple memory cache for search results"""
    
    def __init__(self, ttl_seconds=3600, max_size=100):
        """Initialize cache with TTL and max size
        
        Args:
            ttl_seconds (int): Time-to-live in seconds for cache entries
            max_size (int): Maximum number of entries in cache
        """
        self.cache = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.last_cleanup = datetime.now()
    
    def get(self, key):
        """Get value from cache if not expired
        
        Args:
            key (str): Cache key
            
        Returns:
            Any: Cached value or None if not found or expired
        """
        # Periodically clean up expired entries
        if (datetime.now() - self.last_cleanup).total_seconds() > 600:  # 10 minutes
            self._cleanup()
        
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        if datetime.now() > entry['expires']:
            del self.cache[key]
            return None
            
        return entry['value']
    
    def set(self, key, value):
        """Set value in cache with TTL
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
        """
        # If cache is full, remove oldest item
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['expires'])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=self.ttl_seconds)
        }
    
    def _cleanup(self):
        """Remove expired entries from cache"""
        now = datetime.now()
        self.cache = {k: v for k, v in self.cache.items() if v['expires'] > now}
        self.last_cleanup = now
    
    def clear(self):
        """Clear all cache entries"""
        self.cache = {}
        
    def stats(self):
        """Get cache statistics
        
        Returns:
            dict: Cache statistics
        """
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds
        }

# Create cache instance
cache = SearchCache(ttl_seconds=3600, max_size=100)

# Default search configuration
DEFAULT_SEARCH_CONFIG = {
    'limit': 10,
    'max_retries': 2,
    'min_duration': 0,
    'max_duration': 600,
    'filter_live': True,
    'include_metadata': True,
    'cache_results': True,
    'prefetch_related': True,
    'timeout': 15000  # 15 seconds timeout
}

def parse_duration(duration_str: str) -> int:
    """Parse duration string (e.g. '3:45') to seconds
    
    Args:
        duration_str (str): Duration string in format MM:SS or HH:MM:SS
        
    Returns:
        int: Duration in seconds
    """
    if not duration_str or not isinstance(duration_str, str):
        return 0
        
    parts = duration_str.split(':')
    parts_len = len(parts)
    
    try:
        if parts_len == 2:
            return (int(parts[0]) * 60) + int(parts[1])
        elif parts_len == 3:
            return (int(parts[0]) * 3600) + (int(parts[1]) * 60) + int(parts[2])
    except (ValueError, IndexError):
        pass
        
    return 0

def format_views(views: Union[str, int]) -> str:
    """Format view count (e.g. 1000000 to '1.0M')
    
    Args:
        views (Union[str, int]): View count as string or int
        
    Returns:
        str: Formatted view count
    """
    if not views:
        return ''
        
    try:
        num = int(views) if isinstance(views, str) else views
        if num >= 1000000:
            return f"{(num/1000000):.1f}M"
        elif num >= 1000:
            return f"{(num/1000):.1f}K"
        else:
            return str(num)
    except (ValueError, TypeError):
        return ''

def create_result_object(item: Dict[str, Any], index: int, include_metadata: bool) -> Dict[str, Any]:
    """Create standardized result object from search item
    
    Args:
        item (Dict[str, Any]): Search result item
        index (int): Result index
        include_metadata (bool): Whether to include additional metadata
        
    Returns:
        Dict[str, Any]: Standardized result object
    """
    # Basic result data
    result = {
        'id': index + 1,
        'title': item.get('title', 'Unknown'),
        'url': item.get('link', item.get('url', '')),
        'thumbnail': item.get('thumbnails', [{'url': None}])[0].get('url') if 'thumbnails' in item else None,
        'duration': item.get('duration', 'N/A')
    }
    
    # Add metadata if requested
    if include_metadata:
        result.update({
            'author': item.get('channel', {}).get('name', item.get('channel_name', 'Unknown')),
            'authorUrl': item.get('channel', {}).get('link', None),
            'views': format_views(item.get('viewCount', {}).get('text', item.get('views', ''))),
            'uploadedAt': item.get('publishedTime', item.get('published_time', '')),
            'durationInSeconds': parse_duration(item.get('duration', ''))
        })
        
        # Add description if available
        if 'description' in item and item['description']:
            description = item['description']
            result['description'] = description[:100] + ('...' if len(description) > 100 else '')
    
    return result

async def _search_with_timeout(query: str, search_options: Dict[str, Any], timeout: int) -> Dict[str, Any]:
    """Execute search with timeout
    
    Args:
        query (str): Search query
        search_options (Dict[str, Any]): Search options
        timeout (int): Timeout in milliseconds
        
    Returns:
        Dict[str, Any]: Search results
        
    Raises:
        TimeoutError: If search times out
        Exception: If search fails
    """
    # Create VideosSearch instance in thread-safe manner
    # FIX: Removed proxies parameter by using modified initialization
    loop = asyncio.get_event_loop()
    
    def create_search():
        try:
            # Create VideosSearch without proxies
            search = VideosSearch(query, limit=search_options.get('limit', 15))
            return search.result()
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            raise e
    
    try:
        # Run search with timeout
        timeout_seconds = timeout / 1000  # Convert ms to seconds
        results = await asyncio.wait_for(
            loop.run_in_executor(None, create_search),
            timeout=timeout_seconds
        )
        return results
    except asyncio.TimeoutError:
        raise TimeoutError(f"Search timeout after {timeout}ms")
    except Exception as e:
        logger.error(f"Error in _search_with_timeout: {str(e)}")
        raise e

async def search_videos(query: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Search for YouTube videos with the given query
    
    Args:
        query (str): Search query
        options (Dict[str, Any], optional): Search options
        
    Returns:
        Dict[str, Any]: Search results
        
    Raises:
        ValueError: If query is invalid
    """
    # Validate query
    if not query or not isinstance(query, str):
        raise ValueError('Search query must be a string.')
    
    # Merge options with defaults
    config = DEFAULT_SEARCH_CONFIG.copy()
    if options:
        config.update(options)
    
    # Normalize query
    search_query = query if MUSIC_REGEX.search(query) else f"{query} music"
    cache_key = f"yt_{search_query.lower().replace(' ', '_')}_{config['limit']}"
    
    # Try to get from cache
    if config['cache_results']:
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for \"{search_query}\"")
            return cached_result
    
    logger.info(f"Starting search for \"{search_query}\" with timeout: {config['timeout']}ms")
    
    # Track retry attempts
    attempts = 0
    last_error = None
    
    while attempts < config['max_retries']:
        try:
            logger.info(f"Attempt {attempts + 1} for \"{search_query}\"")
            
            # Set search options
            search_options = {
                'limit': min(config['limit'] + 5, 30),
                'language': 'en',
                'region': 'ID'
            }
            
            # Execute search with timeout
            results = await _search_with_timeout(search_query, search_options, config['timeout'])
            
            # Check if results exist
            if not results or 'result' not in results or not results['result']:
                raise ValueError('No results returned from search')
            
            logger.info(f"Got {len(results['result'])} raw results for \"{search_query}\"")
            
            # Process results
            valid_results = []
            
            for i, item in enumerate(results['result']):
                # Basic validation
                if not item or 'type' not in item or item.get('type') != 'video':
                    continue
                
                # Skip live videos if filtering enabled
                if config['filter_live'] and item.get('isLive', False):
                    continue
                
                # Check duration
                if 'duration' in item:
                    duration = parse_duration(item['duration'])
                    if duration < config['min_duration'] or duration > config['max_duration']:
                        continue
                
                # Format result
                valid_results.append(create_result_object(item, len(valid_results), config['include_metadata']))
                
                # Stop after reaching limit
                if len(valid_results) >= config['limit']:
                    break
            
            logger.info(f"Got {len(valid_results)} valid results for \"{search_query}\"")
            
            # Check if valid results exist
            if not valid_results:
                raise ValueError('No valid results found after filtering')
            
            # Prepare result
            formatted_result = {
                'success': True,
                'query': search_query,
                'totalResults': len(valid_results),
                'results': valid_results
            }
            
            # Save to cache
            if config['cache_results']:
                cache.set(cache_key, formatted_result)
                
                # Optional: Pre-fetch related queries
                if config['prefetch_related'] and valid_results:
                    asyncio.create_task(prefetch_related_queries(search_query, valid_results, config))
            
            return formatted_result
            
        except Exception as error:
            logger.error(f"Search attempt {attempts + 1} failed: {str(error)}")
            last_error = error
            attempts += 1
            
            # If retries remain
            if attempts < config['max_retries']:
                # Exponential backoff
                delay_ms = 1000 * (2 ** attempts)
                logger.info(f"Waiting {delay_ms}ms before next attempt...")
                await asyncio.sleep(delay_ms / 1000)  # Convert ms to seconds
    
    # If all attempts failed
    logger.error(f"All {config['max_retries']} search attempts failed for \"{search_query}\"")
    return {
        'success': False,
        'error': str(last_error) if last_error else 'Search failed after multiple attempts',
        'query': search_query
    }

async def prefetch_related_queries(query: str, results: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
    """Prefetch related search queries
    
    Args:
        query (str): Original search query
        results (List[Dict[str, Any]]): Search results
        config (Dict[str, Any]): Search configuration
    """
    # Find related queries based on titles
    related_queries = set()
    
    # Extract keywords from titles
    for result in results[:2]:
        words = [word for word in result['title'].split() if len(word) > 3][:2]
        
        if len(words) >= 2:
            related_queries.add(f"{words[0]} {words[1]} music")
    
    # Prefetch related queries with low priority
    for related_query in related_queries:
        if related_query != query:
            # Random delay to avoid overloading
            await asyncio.sleep(2 + (3 * asyncio.get_event_loop().time() % 1))
            
            try:
                await search_videos(related_query, {
                    'limit': 5,
                    'include_metadata': False,
                    'prefetch_related': False,
                    'timeout': config['timeout']
                })
            except Exception:
                # Ignore errors in prefetching
                pass

def clear_search_cache() -> Dict[str, Any]:
    """Clear search cache
    
    Returns:
        Dict[str, Any]: Success message
    """
    cache.clear()
    return {'success': True, 'message': 'Cache cleared'}

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics
    
    Returns:
        Dict[str, Any]: Cache statistics
    """
    return cache.stats()