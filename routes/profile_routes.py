from flask import Blueprint, request, jsonify
from controllers.profile_controller import (
    create_profile,
    update_profile,
    get_current_profile,
    get_all_profiles,
    delete_profile
)
from middleware.auth import token_required

# Create blueprint
profile_routes = Blueprint('profile', __name__)

# Create profile (only if one doesn't exist)
@profile_routes.route('/', methods=['POST'])
@token_required
def create_profile_route(current_user):
    return create_profile(request.json, current_user)

# Update profile (only if one exists)
@profile_routes.route('/', methods=['PUT'])
@token_required
def update_profile_route(current_user):
    return update_profile(request.json, current_user)

# Get current user profile
@profile_routes.route('/me', methods=['GET'])
@token_required
def get_current_profile_route(current_user):
    return get_current_profile(current_user)

# Get all profiles
@profile_routes.route('/', methods=['GET'])
@token_required
def get_all_profiles_route(current_user):
    return get_all_profiles()

# Delete profile
@profile_routes.route('/', methods=['DELETE'])
@token_required
def delete_profile_route(current_user):
    return delete_profile(current_user)