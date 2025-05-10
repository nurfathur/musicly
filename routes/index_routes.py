from flask import Blueprint

# Create blueprint
index_bp = Blueprint('index', __name__)
from utils.response import success_response


@index_bp.route('/', methods=['GET'])
def index():
    """
    Index route to verify the API is operational
    """
    return success_response({
        "message": "Welcome to the Audio Processing API!"
    })
