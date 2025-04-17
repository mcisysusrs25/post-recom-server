from flask import jsonify
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from mongo_helper import user_profiles_collection, users_collection

def create_profile(data, current_user):
    """Create user profile - only if one doesn't exist"""
    try:
        name = data.get('name')
        age = data.get('age')
        feed_preferences = data.get('feedPreferences')
        skills = data.get('skills')
        occupation = data.get('occupation')
        user_id = current_user['id']
        
        # First, explicitly check if profile already exists
        existing_profile = user_profiles_collection.find_one({"user": ObjectId(user_id)})
        
        if existing_profile:
            existing_profile['_id'] = str(existing_profile['_id'])
            existing_profile['user'] = str(existing_profile['user'])
            return jsonify({
                "message": "Profile already exists for this user",
                "profile": existing_profile
            }), 400
        
        # Require name for new profile
        if not name:
            return jsonify({"message": "Name is required"}), 400
        
        # Create new profile
        new_profile = {
            "user": ObjectId(user_id),
            "name": name,
            "age": age,
            "feedPreferences": feed_preferences or [],
            "skills": skills or [],
            "occupation": occupation
        }
        
        result = user_profiles_collection.insert_one(new_profile)
        
        # Get created profile
        saved_profile = user_profiles_collection.find_one({"_id": result.inserted_id})
        saved_profile['_id'] = str(saved_profile['_id'])
        saved_profile['user'] = str(saved_profile['user'])
        
        return jsonify(saved_profile), 201
        
    except DuplicateKeyError:
        # Handle race condition - duplicate key error
        return jsonify({"message": "Profile already exists for this user"}), 400
        
    except Exception as error:
        print(f'Profile creation error: {error}')
        return jsonify({"message": "Server error"}), 500

def update_profile(data, current_user):
    """Update user profile - only if one exists"""
    try:
        updates = data
        user_id = current_user['id']
        
        # Find the profile first to verify it exists
        existing_profile = user_profiles_collection.find_one({"user": ObjectId(user_id)})
        
        if not existing_profile:
            return jsonify({"message": "Profile not found. Create a profile first."}), 404
        
        # Apply updates
        valid_fields = ['name', 'age', 'feedPreferences', 'skills', 'occupation']
        update_data = {}
        
        for key in updates:
            if key in valid_fields:
                update_data[key] = updates[key]
        
        if update_data:
            user_profiles_collection.update_one(
                {"user": ObjectId(user_id)},
                {"$set": update_data}
            )
        
        # Get updated profile
        updated_profile = user_profiles_collection.find_one({"user": ObjectId(user_id)})
        updated_profile['_id'] = str(updated_profile['_id'])
        updated_profile['user'] = str(updated_profile['user'])
        
        return jsonify(updated_profile)
        
    except Exception as error:
        print(f'Profile update error: {error}')
        return jsonify({"message": "Server error"}), 500

def get_current_profile(current_user):
    """Get current user profile"""
    try:
        user_id = current_user['id']
        profile = user_profiles_collection.find_one({"user": ObjectId(user_id)})
        
        if not profile:
            return jsonify({"message": "Profile not found"}), 404
        
        # Get user details
        user = users_collection.find_one({"_id": ObjectId(user_id)}, {"email": 1})
        
        # Format response
        profile['_id'] = str(profile['_id'])
        profile['user'] = {"_id": str(profile['user']), "email": user.get('email')}
        
        return jsonify(profile)
        
    except Exception as error:
        print(f'Get profile error: {error}')
        return jsonify({"message": "Server error"}), 500

def get_all_profiles():
    """Get all profiles"""
    try:
        profiles_cursor = user_profiles_collection.find()
        profiles = []
        
        for profile in profiles_cursor:
            # Get user details
            user_id = profile['user']
            user = users_collection.find_one({"_id": user_id}, {"email": 1})
            
            # Format response
            profile['_id'] = str(profile['_id'])
            profile['user'] = {"_id": str(user_id), "email": user.get('email')}
            
            profiles.append(profile)
        
        return jsonify(profiles)
        
    except Exception as error:
        print(f'Get all profiles error: {error}')
        return jsonify({"message": "Server error"}), 500

def delete_profile(current_user):
    """Delete profile"""
    try:
        user_id = current_user['id']
        result = user_profiles_collection.delete_one({"user": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            return jsonify({"message": "Profile not found"}), 404
        
        return jsonify({"message": "Profile deleted successfully"})
        
    except Exception as error:
        print(f'Delete profile error: {error}')
        return jsonify({"message": "Server error"}), 500