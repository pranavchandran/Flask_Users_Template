# __Author__ = "Pranav Chandran"
# __Date__ = 31-05-2023
# __Time__ = 17:49
# __FileName__ = user_views.py
from flask import Blueprint, jsonify, request
from models.user import User


user_blueprint = Blueprint('user', __name__)


# Register a new user
@user_blueprint.route('/register', methods=['POST'])
def register() -> str:
    from app import db
    data: dict = request.get_json()
    name: str = data.get('name')
    email: str = data.get('email')
    mobile: str = data.get('mobile')
    password: str = data.get('password')

    # Validate data
    if not name or not email or not mobile or not password:
        return jsonify(message='Invalid data'), 400
    if User.query.filter_by(email=email).first():
        return jsonify(message='Email already exists'), 400
    if User.query.filter_by(mobile=mobile).first():
        return jsonify(message='Mobile already exists'), 400

    # Validate email and mobile
    if len(mobile) != 10:
        return jsonify(message='Invalid mobile number'), 400
    if '@' not in email:
        return jsonify(message='Invalid email'), 400

    user = User(name=name, email=email, mobile=mobile)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(message='User created successfully'), 201


@user_blueprint.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'mobile': user.mobile
        }
        user_list.append(user_data)
    return jsonify(users=user_list)


# Login a user
@user_blueprint.route('/login', methods=['POST'])
def login() -> str:
    data: dict = request.get_json()
    email: str = data.get('email')
    password: str = data.get('password')
    # Validate data
    if not email or not password:
        return jsonify(message='Invalid data'), 400
    user = User.query.filter_by(email=email).first()
    # Check if user exists and password is correct
    if not user or not user.check_password(password):
        return jsonify(message='Invalid email or password'), 401
    # Generate access token
    access_token = user.generate_access_token()
    # Return access token and user details
    return jsonify(access_token=access_token, user=user.to_dict()), 200
