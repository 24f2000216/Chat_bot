from app import db
from models_db import APIUsage
from flask import current_app
from datetime import datetime, timezone

class RateLimiter:
    """Manages API rate limiting and usage tracking"""
    
    def __init__(self):
        self.warning_threshold = current_app.config.get('USAGE_WARNING_THRESHOLD', 0.80)
    
    def initialize_apis(self):
        """Initialize API usage tracking in database"""
        models_config = current_app.config.get('AVAILABLE_MODELS', {})
        
        for provider, config in models_config.items():
            existing = APIUsage.query.filter_by(api_name=provider).first()
            if not existing:
                usage = APIUsage(
                    api_name=provider,
                    daily_limit=config['daily_limit'],
                    requests_count=0,
                    last_reset=datetime.now(timezone.utc)
                )
                db.session.add(usage)
        db.session.commit()
    
    def check_and_reset_if_needed(self, api_name: str):
        """Reset daily counter if new day (UTC-based)"""
        usage = APIUsage.query.filter_by(api_name=api_name).first()
        if usage and usage.should_reset():
            usage.reset()
    
    def increment_usage(self, api_name: str):
        """Increment request counter for API"""
        self.check_and_reset_if_needed(api_name)
        usage = APIUsage.query.filter_by(api_name=api_name).first()
        if usage:
            usage.requests_count += 1
            db.session.commit()
    
    def get_usage(self, api_name: str) -> dict:
        """Get current usage stats for API"""
        self.check_and_reset_if_needed(api_name)
        usage = APIUsage.query.filter_by(api_name=api_name).first()
        
        if not usage:
            return None
        
        usage_percent = (usage.requests_count / usage.daily_limit) if usage.daily_limit > 0 else 0
        
        return {
            'api_name': api_name,
            'requests_used': usage.requests_count,
            'daily_limit': usage.daily_limit,
            'usage_percent': min(usage_percent, 1.0),
            'remaining': max(0, usage.daily_limit - usage.requests_count),
            'is_near_limit': usage_percent >= self.warning_threshold,
            'is_exhausted': usage_percent >= 1.0
        }
    
    def get_all_usage(self) -> dict:
        """Get usage stats for all APIs"""
        models_config = current_app.config.get('AVAILABLE_MODELS', {})
        all_usage = {}
        
        for provider in models_config.keys():
            all_usage[provider] = self.get_usage(provider)
        
        return all_usage
    
    def get_best_available_model(self) -> str:
        """Return API with lowest usage that's not exhausted"""
        all_usage = self.get_all_usage()
        
        # Filter out exhausted models
        available = {
            name: stats for name, stats in all_usage.items()
            if stats and not stats['is_exhausted']
        }
        
        if not available:
            return None
        
        # Return model with lowest usage percent
        return min(available.items(), key=lambda x: x[1]['usage_percent'])[0]
    
    def is_api_available(self, api_name: str) -> bool:
        """Check if API is available (not exhausted)"""
        usage = self.get_usage(api_name)
        return usage and not usage['is_exhausted']