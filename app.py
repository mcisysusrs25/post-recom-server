from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Import MongoDB connection
from mongo_helper import client as mongo_client

# Import routes
from routes.auth_routes import auth_routes
from routes.profile_routes import profile_routes
from routes.post_routes import post_routes

# Initialize Flask
app = Flask(__name__)

# Middleware
CORS(app)
app.json.sort_keys = False  # Preserve JSON response order

# Set up logging
logging.basicConfig(level=logging.INFO)

# Test MongoDB connection
print('Connecting to MongoDB...')
try:
    # Test the connection
    mongo_client.admin.command('ping')
    print('Connected to MongoDB')
except Exception as e:
    print('MongoDB connection error details:', {
        'message': str(e),
        'code': getattr(e, 'code', None),
        'name': e.__class__.__name__
    })
    print('Please check your connection string and credentials')

# routes
app.register_blueprint(auth_routes, url_prefix='/api/auth')
app.register_blueprint(profile_routes, url_prefix='/api/profiles')
app.register_blueprint(post_routes, url_prefix='/api/posts')

# Default route
@app.route('/')
def index():
    return 'Recommendation System API is running'

# Error handling
@app.errorhandler(500)
def server_error(error):
    app.logger.error(f'Server error: {error}')
    return jsonify({'message': 'Something went wrong!'}), 500

# Start server
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=True)