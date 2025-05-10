from flask import jsonify

def success_response(data, status_code=200):
    """Create a standardized success response
    
    Args:
        data (dict): Response data
        status_code (int): HTTP status code
        
    Returns:
        Response: Flask response object
    """
    response = {
        "success": True,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message, status_code=400):
    """Create a standardized error response
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        
    Returns:
        Response: Flask response object
    """
    response = {
        "success": False,
        "error": message
    }
    return jsonify(response), status_code