from datetime import datetime, timezone
from app import db

class APIUsage(db.Model):
    """Track daily API usage for rate limiting"""
    __tablename__ = 'api_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(50), unique=True, nullable=False)
    requests_count = db.Column(db.Integer, default=0)
    daily_limit = db.Column(db.Integer, nullable=False)
    last_reset = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<APIUsage {self.api_name}: {self.requests_count}/{self.daily_limit}>'
    
    def should_reset(self):
        """Check if daily limit should be reset (UTC-based)"""
        now_utc = datetime.now(timezone.utc)
        return (now_utc.date() > self.last_reset.date())
    
    def reset(self):
        """Reset daily counter"""
        self.requests_count = 0
        self.last_reset = datetime.now(timezone.utc)
        db.session.commit()

class Conversation(db.Model):
    """Store conversation history"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    model_used = db.Column(db.String(50), nullable=False)
    tokens_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Conversation {self.session_id}: {self.model_used}>'

class AvailableModel(db.Model):
    """Configuration for available AI models"""
    __tablename__ = 'available_models'
    
    id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    model_id = db.Column(db.String(100), nullable=False)
    daily_limit = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<AvailableModel {self.model_name}>'