from flask import Flask
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
app = Flask(__name__)

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Register routes
    from routes.audio_routes import audio_bp
    from routes.health_routes import health_bp
    from routes.index_routes import index_bp
    
    app.register_blueprint(index_bp, url_prefix='')
    app.register_blueprint(audio_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    
    return app


if __name__ == '__main__':
    app = create_app()
    # Set up server configuration
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('ENVIRONMENT', 'production').lower() == 'development'
    
    logger.info(f"Starting server on port {port}, debug mode: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)