from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config.settings import Config
from routes import chat_bp, models_bp, usage_bp, health_bp

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app)
    
    with app.app_context():
        db.create_all()
    
    app.register_blueprint(chat_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(usage_bp)
    app.register_blueprint(health_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)