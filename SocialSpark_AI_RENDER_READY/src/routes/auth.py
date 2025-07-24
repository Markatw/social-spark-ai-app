from flask import Blueprint, request, jsonify
from src.models.user import db, User
import jwt
import datetime
import os
import re
import html

auth_bp = Blueprint("auth_bp", __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def sanitize_input(text):
    """Sanitize input to prevent XSS"""
    if not text:
        return text
    # Remove HTML tags and escape special characters
    text = re.sub(r'<[^>]*>', '', text)
    text = html.escape(text)
    return text.strip()

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"message": "Missing username, email, or password"}), 400

    # Sanitize inputs
    username = sanitize_input(username)
    email = sanitize_input(email)

    # Validate input lengths
    if len(username) > 80:
        return jsonify({"message": "Username must be 80 characters or less"}), 400
    if len(email) > 120:
        return jsonify({"message": "Email must be 120 characters or less"}), 400

    # Validate email format
    if not validate_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    # Validate password strength
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({"message": message}), 400

    # Check for existing user
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User with that email already exists"}), 409
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    # Sanitize email input
    email = sanitize_input(email)

    # Validate email format
    if not validate_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, os.environ.get("SECRET_KEY", "supersecretkey"), algorithm="HS256")

    return jsonify({"message": "Login successful", "token": token}), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    # In a stateless JWT system, logout is handled client-side by removing the token
    # For enhanced security, we could implement a token blacklist
    return jsonify({"message": "Logout successful"}), 200


