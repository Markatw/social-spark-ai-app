from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from models.user import User
from models.content import Content
from models.user import db
from datetime import datetime

content_bp = Blueprint("content_bp", __name__)

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

@content_bp.route("/save", methods=["POST"])
@token_required
def save_content(current_user):
    """Save generated content"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['content', 'platform', 'content_type', 'topic']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"message": f"Missing required field: {field}"}), 400
        
        # Create new content record
        new_content = Content(
            user_id=current_user.id,
            topic=data['topic'],
            content=data['content'],
            platform=data['platform'],
            content_type=data['content_type'],
            tone=data.get('tone', 'casual'),
            style=data.get('style', 'engaging'),
            keywords=data.get('keywords', '')
        )
        
        db.session.add(new_content)
        db.session.commit()
        
        return jsonify({
            "message": "Content saved successfully",
            "content": new_content.to_dict()
        }), 201
        
    except Exception as e:
        print(f"Save content error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to save content"}), 500

@content_bp.route("/saved", methods=["GET"])
@token_required
def get_saved_content(current_user):
    """Get user's saved content with pagination and filtering"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        platform = request.args.get('platform')
        content_type = request.args.get('content_type')
        search = request.args.get('search')
        
        # Build query
        query = Content.query.filter_by(user_id=current_user.id)
        
        if platform:
            query = query.filter(Content.platform == platform)
        
        if content_type:
            query = query.filter(Content.content_type == content_type)
        
        if search:
            query = query.filter(
                db.or_(
                    Content.topic.contains(search),
                    Content.content.contains(search),
                    Content.keywords.contains(search)
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(Content.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        content_list = [content.to_dict() for content in pagination.items]
        
        return jsonify({
            "content": content_list,
            "pagination": {
                "page": page,
                "pages": pagination.pages,
                "per_page": per_page,
                "total": pagination.total,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        print(f"Get saved content error: {str(e)}")
        return jsonify({"message": "Failed to fetch saved content"}), 500

@content_bp.route("/recent", methods=["GET"])
@token_required
def get_recent_content(current_user):
    """Get user's recent content"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        recent_content = Content.query.filter_by(user_id=current_user.id)\
            .order_by(Content.created_at.desc())\
            .limit(limit)\
            .all()
        
        content_list = [content.to_dict() for content in recent_content]
        
        return jsonify({"content": content_list}), 200
        
    except Exception as e:
        print(f"Get recent content error: {str(e)}")
        return jsonify({"message": "Failed to fetch recent content"}), 500

@content_bp.route("/<int:content_id>", methods=["GET"])
@token_required
def get_content(current_user, content_id):
    """Get specific content by ID"""
    try:
        content = Content.query.filter_by(
            id=content_id, 
            user_id=current_user.id
        ).first()
        
        if not content:
            return jsonify({"message": "Content not found"}), 404
        
        return jsonify({"content": content.to_dict()}), 200
        
    except Exception as e:
        print(f"Get content error: {str(e)}")
        return jsonify({"message": "Failed to fetch content"}), 500

@content_bp.route("/<int:content_id>", methods=["PUT"])
@token_required
def update_content(current_user, content_id):
    """Update specific content"""
    try:
        content = Content.query.filter_by(
            id=content_id, 
            user_id=current_user.id
        ).first()
        
        if not content:
            return jsonify({"message": "Content not found"}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'topic' in data:
            content.topic = data['topic']
        if 'content' in data:
            content.content = data['content']
        if 'platform' in data:
            content.platform = data['platform']
        if 'content_type' in data:
            content.content_type = data['content_type']
        if 'tone' in data:
            content.tone = data['tone']
        if 'style' in data:
            content.style = data['style']
        if 'keywords' in data:
            content.keywords = data['keywords']
        
        content.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "message": "Content updated successfully",
            "content": content.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Update content error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to update content"}), 500

@content_bp.route("/<int:content_id>", methods=["DELETE"])
@token_required
def delete_content(current_user, content_id):
    """Delete specific content"""
    try:
        content = Content.query.filter_by(
            id=content_id, 
            user_id=current_user.id
        ).first()
        
        if not content:
            return jsonify({"message": "Content not found"}), 404
        
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({"message": "Content deleted successfully"}), 200
        
    except Exception as e:
        print(f"Delete content error: {str(e)}")
        db.session.rollback()
        return jsonify({"message": "Failed to delete content"}), 500

@content_bp.route("/export", methods=["GET"])
@token_required
def export_content(current_user):
    """Export user's content in various formats"""
    try:
        format_type = request.args.get('format', 'json').lower()
        
        # Get all user content
        content_list = Content.query.filter_by(user_id=current_user.id)\
            .order_by(Content.created_at.desc())\
            .all()
        
        if format_type == 'json':
            import json
            data = {
                "user": current_user.username,
                "export_date": datetime.utcnow().isoformat(),
                "total_content": len(content_list),
                "content": [content.to_dict() for content in content_list]
            }
            
            response = jsonify(data)
            response.headers['Content-Disposition'] = 'attachment; filename=content_export.json'
            return response
            
        elif format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['ID', 'Topic', 'Content', 'Platform', 'Content Type', 'Tone', 'Style', 'Keywords', 'Created At'])
            
            # Write data
            for content in content_list:
                writer.writerow([
                    content.id,
                    content.topic,
                    content.content,
                    content.platform,
                    content.content_type,
                    content.tone,
                    content.style,
                    content.keywords,
                    content.created_at.isoformat() if content.created_at else ''
                ])
            
            output.seek(0)
            
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=content_export.csv'}
            )
        
        else:
            return jsonify({"message": "Unsupported export format"}), 400
            
    except Exception as e:
        print(f"Export content error: {str(e)}")
        return jsonify({"message": "Failed to export content"}), 500

@content_bp.route("/stats", methods=["GET"])
@token_required
def get_content_stats(current_user):
    """Get content statistics for the user"""
    try:
        total_content = Content.query.filter_by(user_id=current_user.id).count()
        
        # Get platform breakdown
        from sqlalchemy import func
        platform_stats = db.session.query(
            Content.platform,
            func.count(Content.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(Content.platform).all()
        
        # Get content type breakdown
        type_stats = db.session.query(
            Content.content_type,
            func.count(Content.id).label('count')
        ).filter_by(user_id=current_user.id).group_by(Content.content_type).all()
        
        # Get recent activity (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = Content.query.filter(
            Content.user_id == current_user.id,
            Content.created_at >= week_ago
        ).count()
        
        return jsonify({
            "total_content": total_content,
            "recent_content": recent_count,
            "platform_breakdown": [{"platform": p, "count": c} for p, c in platform_stats],
            "type_breakdown": [{"type": t, "count": c} for t, c in type_stats]
        }), 200
        
    except Exception as e:
        print(f"Get content stats error: {str(e)}")
        return jsonify({"message": "Failed to fetch content statistics"}), 500

