import asyncio
import sys
import json
import logging

# Import your controller
from controllers.youtube_controller import YouTubeController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_controller():
    """Test the YouTube controller"""
    try:
        # Initialize controller
        controller = YouTubeController()
        
        # Test 1: Basic search
        print("\n=== Test 1: Basic Search ===")
        query = "coldplay"
        print(f"Searching for: {query}")
        response, status_code = await controller.search(query)
        
        # Parse the response JSON
        if isinstance(response, str):
            response_data = json.loads(response)
        else:
            response_data = response
            
        print(f"Status code: {status_code}")
        if status_code == 200:
            print(f"✅ Search successful!")
            data = response_data.get('data', {})
            print(f"Total results: {data.get('totalResults', 0)}")
            
            # Print first result if available
            results = data.get('results', [])
            if results:
                first_result = results[0]
                print("\nFirst result:")
                print(f"Title: {first_result.get('title')}")
                print(f"URL: {first_result.get('url')}")
                print(f"Duration: {first_result.get('duration')}")
                print(f"Author: {first_result.get('author', 'Unknown')}")
        else:
            print(f"❌ Search failed: {response_data.get('error', 'Unknown error')}")
        
        # Test 2: Cache stats
        print("\n=== Test 2: Cache Stats ===")
        response, status_code = controller.get_cache_statistics()
        
        # Parse the response JSON
        if isinstance(response, str):
            response_data = json.loads(response)
        else:
            response_data = response
            
        print(f"Status code: {status_code}")
        if status_code == 200:
            print(f"✅ Got cache stats successfully!")
            cache_stats = response_data.get('data', {}).get('cache', {})
            print(f"Cache size: {cache_stats.get('size', 0)}")
            print(f"Cache max size: {cache_stats.get('max_size', 0)}")
            print(f"Cache TTL: {cache_stats.get('ttl_seconds', 0)} seconds")
        else:
            print(f"❌ Failed to get cache stats: {response_data.get('error', 'Unknown error')}")
        
        # Test 3: Clear cache
        print("\n=== Test 3: Clear Cache ===")
        response, status_code = controller.clear_cache()
        
        # Parse the response JSON
        if isinstance(response, str):
            response_data = json.loads(response)
        else:
            response_data = response
            
        print(f"Status code: {status_code}")
        if status_code == 200:
            print(f"✅ Cache cleared successfully!")
        else:
            print(f"❌ Failed to clear cache: {response_data.get('error', 'Unknown error')}")
        
        # Test 4: Empty query (should fail with 400)
        print("\n=== Test 4: Empty Query (Expected to fail) ===")
        response, status_code = await controller.search("")
        
        # Parse the response JSON
        if isinstance(response, str):
            response_data = json.loads(response)
        else:
            response_data = response
            
        print(f"Status code: {status_code}")
        if status_code == 400:
            print(f"✅ Correctly rejected empty query with 400 status")
            print(f"Error message: {response_data.get('error', 'No error message')}")
        else:
            print(f"❌ Expected 400 status code, got {status_code}")
            
    except Exception as e:
        print(f"❌ Error during controller test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_controller())