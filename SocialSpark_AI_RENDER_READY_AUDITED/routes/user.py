from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
from models.content import Content
from models.user import db
from datetime import datetime, timedelta
import json

user_bp = Blueprint("user_bp", __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for x-access-token header
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        # Check for Authorization Bearer header
        elif "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, os.environ.get("SECRET_KEY", "supersecretkey"), algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                return jsonify({"message": "User not found!"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@user_bp.route("/profile", methods=["GET"])
@token_required
def get_user_profile(current_user):
    """Get user profile with statistics"""
    try:
        # Calculate user statistics
        total_content = Content.query.filter_by(user_id=current_user.id).count()
        
        # Get unique platforms used
        from sqlalchemy import func
        platforms = Content.query.filter_by(user_id=current_user.id)\
            .with_entities(Content.platform).distinct().count()
        
        # Get content this month
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month = Content.query.filter(
            Content.user_id == current_user.id,
            Content.created_at >= month_start
        ).count()
        
        # Calculate streak (simplified - consecutive days with content)
        streak = 0  # Placeholder for now
        
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "bio": getattr(current_user, 'bio', ''),
            "location": getattr(current_user, 'location', ''),
            "website": getattr(current_user, 'website', ''),
            "avatar": getattr(current_user, 'avatar', ''),
            "joinDate": current_user.created_at.isoformat() if current_user.created_at else None,
            "stats": {
                "totalContent": total_content,
                "platforms": platforms,
                "thisMonth": this_month,
                "streak": streak
            }
        }
        
        return jsonify({"user": user_data}), 200
        
    except Exception as e:
        print(f"Get profile error: {str(e)}")
        return jsonify({"message": "Failed to fetch profile"}), 500

@user_bp.route("/profile", methods=["PUT"])
@token_required
def update_user_profile(current_user):
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Update allowed fields
        if 'username' in data:
            # Check if username is already taken
            existing_user = User.query.filter(
                User.username == data['username'],
                User.id != current_user.id
            ).first()
            if existing_user:
                return jsonify({"message": "Username already taken"}), 400
            current_user.username = data['username']
        
        if 'bio' in data:
            current_user.bio = data['bio']
        if 'location' in data:
            current_user.location = data['location']
        if 'website' in data:
            current_user.website = data['website']
        
        db.session.commit()
        
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        print(f"Update profile error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to update profile"}), 500

@user_bp.route("/avatar", methods=["POST"])
@token_required
def upload_avatar(current_user):
    """Upload user avatar"""
    try:
        if 'avatar' not in request.files:
            return jsonify({"message": "No avatar file provided"}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({"message": "No file selected"}), 400
        
        # For now, just return a placeholder URL
        # In production, you would upload to cloud storage
        avatar_url = f"/static/avatars/{current_user.id}_{file.filename}"
        current_user.avatar = avatar_url
        
        db.session.commit()
        
        return jsonify({
            "message": "Avatar uploaded successfully",
            "avatarUrl": avatar_url
        }), 200
        
    except Exception as e:
        print(f"Upload avatar error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to upload avatar"}), 500

@user_bp.route("/settings", methods=["GET"])
@token_required
def get_user_settings(current_user):
    """Get user settings"""
    try:
        # Default settings if not stored in database
        default_settings = {
            "theme": "system",
            "language": "en",
            "notifications": {
                "email": True,
                "push": False,
                "marketing": False
            },
            "privacy": {
                "profilePublic": False,
                "showStats": True,
                "allowAnalytics": True
            },
            "defaults": {
                "platform": "instagram",
                "tone": "casual",
                "contentType": "post"
            }
        }
        
        # In production, you would store these in the database
        settings = getattr(current_user, 'settings', default_settings)
        if isinstance(settings, str):
            settings = json.loads(settings)
        
        return jsonify({"settings": settings}), 200
        
    except Exception as e:
        print(f"Get settings error: {str(e)}")
        return jsonify({"message": "Failed to fetch settings"}), 500

@user_bp.route("/settings", methods=["PUT"])
@token_required
def update_user_settings(current_user):
    """Update user settings"""
    try:
        data = request.get_json()
        
        # Store settings as JSON string in user model
        # In production, you might want a separate settings table
        current_user.settings = json.dumps(data)
        
        db.session.commit()
        
        return jsonify({"message": "Settings updated successfully"}), 200
        
    except Exception as e:
        print(f"Update settings error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to update settings"}), 500

@user_bp.route("/change-password", methods=["POST"])
@token_required
def change_password(current_user):
    """Change user password"""
    try:
        data = request.get_json()
        
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        
        if not current_password or not new_password:
            return jsonify({"message": "Current and new passwords are required"}), 400
        
        # Verify current password
        if not check_password_hash(current_user.password, current_password):
            return jsonify({"message": "Current password is incorrect"}), 400
        
        # Validate new password
        if len(new_password) < 8:
            return jsonify({"message": "New password must be at least 8 characters long"}), 400
        
        # Update password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({"message": "Password changed successfully"}), 200
        
    except Exception as e:
        print(f"Change password error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to change password"}), 500

@user_bp.route("/export", methods=["GET"])
@token_required
def export_user_data(current_user):
    """Export all user data"""
    try:
        # Get all user content
        content_list = Content.query.filter_by(user_id=current_user.id).all()
        
        # Prepare export data
        export_data = {
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "bio": getattr(current_user, 'bio', ''),
                "location": getattr(current_user, 'location', ''),
                "website": getattr(current_user, 'website', ''),
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None
            },
            "content": [content.to_dict() for content in content_list],
            "export_info": {
                "export_date": datetime.utcnow().isoformat(),
                "total_content": len(content_list),
                "version": "1.0"
            }
        }
        
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = 'attachment; filename=socialspark_data_export.json'
        return response
        
    except Exception as e:
        print(f"Export data error: {str(e)}")
        return jsonify({"message": "Failed to export data"}), 500

@user_bp.route("/delete", methods=["DELETE"])
@token_required
def delete_user_account(current_user):
    """Delete user account and all associated data"""
    try:
        # Delete all user content first
        Content.query.filter_by(user_id=current_user.id).delete()
        
        # Delete user account
        db.session.delete(current_user)
        db.session.commit()
        
        return jsonify({"message": "Account deleted successfully"}), 200
        
    except Exception as e:
        print(f"Delete account error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to delete account"}), 500

@user_bp.route("/stats", methods=["GET"])
@token_required
def get_user_stats(current_user):
    """Get detailed user statistics"""
    try:
        # Basic stats
        total_content = Content.query.filter_by(user_id=current_user.id).count()
        
        # Platform usage
        from sqlalchemy import func
        platform_usage = db.session.query(
            Content.platform,
            func.count(Content.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(Content.platform).all()
        
        # Content type usage
        type_usage = db.session.query(
            Content.content_type,
            func.count(Content.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(Content.content_type).all()
        
        # Recent activity
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_activity = Content.query.filter(
            Content.user_id == current_user.id,
            Content.created_at >= week_ago
        ).count()
        
        return jsonify({
            "total_content": total_content,
            "recent_activity": recent_activity,
            "platform_usage": [{"platform": p, "count": c} for p, c in platform_usage],
            "type_usage": [{"type": t, "count": c} for t, c in type_usage],
            "account_age_days": (datetime.utcnow() - current_user.created_at).days if current_user.created_at else 0
        }), 200
        
    except Exception as e:
        print(f"Get user stats error: {str(e)}")
        return jsonify({"message": "Failed to fetch user statistics"}), 500

