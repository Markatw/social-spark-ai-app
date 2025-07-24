import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.content import content_bp
from src.routes.generate import generate_bp
from src.routes.analytics import analytics_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app, origins="*", supports_credentials=False)
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Register all blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(content_bp, url_prefix='/api/content')
app.register_blueprint(generate_bp, url_prefix='/api/generate')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

# Health check endpoint
@app.route('/api/health')
def health_check():
    return {"message": "SocialSpark AI API is running", "status": "healthy"}

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
