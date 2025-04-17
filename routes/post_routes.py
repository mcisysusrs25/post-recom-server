from flask import Blueprint, request, jsonify
from controllers.post_controller import (
    create_post, 
    get_all_posts, 
    get_posts_by_tag, 
    get_user_posts, 
    get_post_by_id, 
    update_post, 
    delete_post, 
    like_post, 
    unlike_post, 
    view_post
)
from middleware.auth import token_required

# Create blueprint
post_routes = Blueprint('post', __name__)

# Create a post
@post_routes.route('/', methods=['POST'])
@token_required
def create_post_route(current_user):
    return create_post(request.json, current_user)

# Get all posts
@post_routes.route('/', methods=['GET'])
@token_required
def get_all_posts_route(current_user):
    return get_all_posts(current_user)

# Get posts by tag
@post_routes.route('/tag/<tag>', methods=['GET'])
@token_required
def get_posts_by_tag_route(current_user, tag):
    return get_posts_by_tag(tag, current_user)

# Get posts by current user
@post_routes.route('/myPosts', methods=['GET'])
@token_required
def get_user_posts_route(current_user):
    return get_user_posts(current_user)

# Get post by ID
@post_routes.route('/<id>', methods=['GET'])
@token_required
def get_post_by_id_route(current_user, id):
    return get_post_by_id(id, current_user)

# Update a post
@post_routes.route('/<id>', methods=['PUT'])
@token_required
def update_post_route(current_user, id):
    return update_post(id, request.json, current_user)

# Delete a post
@post_routes.route('/<id>', methods=['DELETE'])
@token_required
def delete_post_route(current_user, id):
    return delete_post(id, current_user)

# Like a post
@post_routes.route('/<id>/like', methods=['POST'])
@token_required
def like_post_route(current_user, id):
    return like_post(id, current_user)

# Unlike a post
@post_routes.route('/<id>/like', methods=['DELETE'])
@token_required
def unlike_post_route(current_user, id):
    return unlike_post(id, current_user)

# View a post
@post_routes.route('/<id>/view', methods=['POST'])
@token_required
def view_post_route(current_user, id):
    return view_post(id, current_user)