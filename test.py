import asyncio
from flask import Flask, jsonify
import logging

# Import your controller
from controllers.youtube_controller import YouTubeController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

async def test_controller():
    """Test YouTube controller with basic search"""
    print("=== Test 1: Basic Search ===")
    controller = YouTubeController()
    query = "coldplay"
    print(f"Searching for: {query}")
    
    # Create Flask app context for jsonify
    with app.app_context():
        try:
            response, status_code = await controller.search(query)
            if status_code == 200:
                print(f"✅ Success! Found {response.json.get('totalResults', 0)} results")
                # Print first result
                if response.json.get('results'):
                    first_result = response.json['results'][0]
                    print(f"First result: {first_result.get('title')}")
                    print(f"Duration: {first_result.get('duration')}")
            else:
                print(f"❌ Error: {response.json.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Error during controller test: {str(e)}")
            import traceback
            traceback.print_exc()

async def test_direct_service():
    """Test YouTube service directly"""
    print("\n=== Test 2: Direct Service Call ===")
    from services.youtube import search_videos

    query = "adele"
    print(f"Searching service directly for: {query}")
    
    try:
        result = await search_videos(query)
        if result.get('success'):
            print(f"✅ Success! Found {result.get('totalResults', 0)} results")
            # Print first result
            if result.get('results'):
                first_result = result['results'][0]
                print(f"First result: {first_result.get('title')}")
                print(f"Duration: {first_result.get('duration')}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error during service test: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    await test_controller()
    await test_direct_service()

if __name__ == "__main__":
    asyncio.run(main())