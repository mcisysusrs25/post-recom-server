import jwt
import os
from flask import request, jsonify
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from header
        token = request.headers.get('x-auth-token')
        if not token:
            return jsonify({'message': 'No token, authorization denied'}), 401
        
        try:
            # Verify token
            decoded = jwt.decode(token, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
            # Pass decoded user to the function
            return f(decoded, *args, **kwargs)
        except Exception as e:
            print(f"Token verification error: {e}")
            return jsonify({'message': 'Token is not valid'}), 401
            
    return decorated