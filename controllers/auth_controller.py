import os
import jwt
import bcrypt
from flask import jsonify
from bson import ObjectId

# Import MongoDB collections from helper
from mongo_helper import users_collection

def register(data):
    """Register a new user"""
    try:
        email = data.get('email')
        password = data.get('password')
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": email.lower()})
        if existing_user:
            return jsonify({"message": "User already exists"}), 400
        
        # Hash password
        salt = bcrypt.gensalt(10)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Create new user
        new_user = {
            "email": email.lower(),
            "password": hashed_password
        }
        
        result = users_collection.insert_one(new_user)
        new_user_id = result.inserted_id
        
        # Generate JWT token valid for 1 week
        token = jwt.encode(
            {"id": str(new_user_id), "email": email},
            os.environ.get('JWT_SECRET'),
            algorithm="HS256"
        )
        
        return jsonify({
            "token": token,
            "user": {
                "id": str(new_user_id),
                "email": email
            }
        }), 201
        
    except Exception as error:
        print(f'Registration error: {error}')
        return jsonify({"message": "Registration failed"}), 500

def login(data):
    """Login a user"""
    try:
        email = data.get('email')
        password = data.get('password')
        
        # Find user by email
        user = users_collection.find_one({"email": email.lower()})
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Check password
        is_match = bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        )
        
        if not is_match:
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Generate JWT token valid for 1 week
        token = jwt.encode(
            {"id": str(user['_id']), "email": user['email']},
            os.environ.get('JWT_SECRET'),
            algorithm="HS256"
        )
        
        return jsonify({
            "token": token,
            "user": {
                "id": str(user['_id']),
                "email": user['email']
            }
        })
        
    except Exception as error:
        print(f'Login error: {error}')
        return jsonify({"message": "Login failed"}), 500

def get_current_user(current_user):
    """Get current user data"""
    try:
        # Get user without password
        user = users_collection.find_one({"_id": ObjectId(current_user['id'])})
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Remove password from user data
        user.pop('password', None)
        
        # Convert ObjectId to string
        user['_id'] = str(user['_id'])
        
        return jsonify(user)
        
    except Exception as error:
        print(f'Get current user error: {error}')
        return jsonify({"message": "Failed to get user data"}), 500