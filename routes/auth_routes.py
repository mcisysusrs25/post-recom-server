from flask import Blueprint, request, jsonify
from controllers.auth_controller import register, login, get_current_user
from middleware.auth import token_required

# Create blueprint
auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['POST'])
def register_route():
    return register(request.json)

@auth_routes.route('/login', methods=['POST'])
def login_route():
    return login(request.json)

@auth_routes.route('/me', methods=['GET'])
@token_required
def get_current_user_route(current_user):
    return get_current_user(current_user)