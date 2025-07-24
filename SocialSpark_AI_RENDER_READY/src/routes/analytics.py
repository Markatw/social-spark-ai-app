from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
import os
from datetime import datetime, timedelta
from src.models.user import User
from src.models.content import Content
from sqlalchemy import func

analytics_bp = Blueprint("analytics_bp", __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, os.environ.get("SECRET_KEY", "supersecretkey"), algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@analytics_bp.route("/dashboard", methods=["GET"])
@token_required
def get_dashboard_analytics(current_user):
    """Get dashboard analytics data"""
    try:
        # Calculate date ranges
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Get basic stats
        total_content = Content.query.filter_by(user_id=current_user.id).count()
        this_week = Content.query.filter(
            Content.user_id == current_user.id,
            Content.created_at >= week_ago
        ).count()
        
        # Get unique platforms
        platforms = Content.query.filter_by(user_id=current_user.id).with_entities(Content.platform).distinct().count()
        
        # Calculate average per day
        if total_content > 0:
            days_since_first = (today - current_user.created_at.date()).days + 1
            avg_per_day = round(total_content / days_since_first, 1)
        else:
            avg_per_day = 0

        # Get platform distribution data
        platform_data = []
        platform_counts = Content.query.filter_by(user_id=current_user.id).with_entities(
            Content.platform, func.count(Content.id)
        ).group_by(Content.platform).all()
        
        for platform, count in platform_counts:
            platform_data.append({
                "name": platform.title(),
                "value": count
            })

        # Get weekly activity data
        weekly_data = []
        for i in range(7):
            date = today - timedelta(days=6-i)
            count = Content.query.filter(
                Content.user_id == current_user.id,
                func.date(Content.created_at) == date
            ).count()
            weekly_data.append({
                "day": date.strftime("%a"),
                "content": count
            })

        return jsonify({
            "stats": {
                "totalContent": total_content,
                "thisWeek": this_week,
                "platforms": platforms,
                "avgPerDay": avg_per_day
            },
            "platformData": platform_data,
            "weeklyData": weekly_data
        }), 200

    except Exception as e:
        print(f"Analytics error: {str(e)}")
        return jsonify({"message": "Failed to fetch analytics"}), 500

@analytics_bp.route("/content", methods=["GET"])
@token_required
def get_content_analytics(current_user):
    """Get detailed content analytics"""
    try:
        # Get content type distribution
        content_types = Content.query.filter_by(user_id=current_user.id).with_entities(
            Content.content_type, func.count(Content.id)
        ).group_by(Content.content_type).all()

        type_data = []
        for content_type, count in content_types:
            type_data.append({
                "type": content_type.title(),
                "count": count
            })

        # Get monthly trends
        monthly_data = []
        for i in range(6):
            date = datetime.now().replace(day=1) - timedelta(days=30*i)
            month_start = date.replace(day=1)
            if i == 0:
                month_end = datetime.now()
            else:
                next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
                month_end = next_month - timedelta(days=1)
            
            count = Content.query.filter(
                Content.user_id == current_user.id,
                Content.created_at >= month_start,
                Content.created_at <= month_end
            ).count()
            
            monthly_data.insert(0, {
                "month": month_start.strftime("%b"),
                "content": count
            })

        return jsonify({
            "typeData": type_data,
            "monthlyData": monthly_data
        }), 200

    except Exception as e:
        print(f"Content analytics error: {str(e)}")
        return jsonify({"message": "Failed to fetch content analytics"}), 500

@analytics_bp.route("/usage", methods=["GET"])
@token_required
def get_usage_analytics(current_user):
    """Get user usage statistics"""
    try:
        # Calculate usage metrics
        total_sessions = 1  # Placeholder - would need session tracking
        avg_session_time = "5m 30s"  # Placeholder
        most_used_platform = "Instagram"  # Placeholder
        
        # Get most productive day
        day_counts = {}
        contents = Content.query.filter_by(user_id=current_user.id).all()
        
        for content in contents:
            day = content.created_at.strftime("%A")
            day_counts[day] = day_counts.get(day, 0) + 1
        
        most_productive_day = max(day_counts, key=day_counts.get) if day_counts else "Monday"

        return jsonify({
            "totalSessions": total_sessions,
            "avgSessionTime": avg_session_time,
            "mostUsedPlatform": most_used_platform,
            "mostProductiveDay": most_productive_day,
            "dayBreakdown": day_counts
        }), 200

    except Exception as e:
        print(f"Usage analytics error: {str(e)}")
        return jsonify({"message": "Failed to fetch usage analytics"}), 500

