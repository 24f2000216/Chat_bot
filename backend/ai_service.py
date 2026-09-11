from adapter_factory import AdapterFactory
from rate_limiter import RateLimiter
from models_db import Conversation
from app import db
import uuid
from datetime import datetime, timezone

class AIService:
    """Main service for handling chat requests"""
    
    def __init__(self):
        self.adapter_factory = AdapterFactory()
        self.rate_limiter = RateLimiter()
        self.current_model = None
    
    def send_message(self, user_message: str, session_id: str = None, preferred_model: str = None) -> dict:
        """
        Send message and get response from best available API.
        
        Returns:
        {
            'response': 'AI response text',
            'model_used': 'which model was used',
            'session_id': 'session identifier',
            'warning': 'warning message if model switched or near limit',
            'status': 'success' or 'error'
        }
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        try:
            # Check if preferred model is available
            if preferred_model:
                if self.rate_limiter.is_api_available(preferred_model):
                    model_to_use = preferred_model
                else:
                    # Preferred model exhausted, find alternative
                    model_to_use = self.rate_limiter.get_best_available_model()
                    warning = f"Preferred model {preferred_model} exhausted. Switched to {model_to_use}"
            else:
                # Auto-select best model
                model_to_use = self.rate_limiter.get_best_available_model()
            
            if not model_to_use:
                return {
                    'status': 'error',
                    'response': 'All API models have reached daily limits. Please try again tomorrow.',
                    'model_used': None,
                    'session_id': session_id
                }
            
            # Check if model is near limit
            usage = self.rate_limiter.get_usage(model_to_use)
            warning = None
            if usage['is_near_limit'] and not usage['is_exhausted']:
                warning = f"Model {model_to_use} is at {usage['usage_percent']:.1%} usage. You may need to switch soon."
            
            # Get adapter and send message
            adapter = self.adapter_factory.get_adapter(model_to_use)
            
            # Format message (simple format for now)
            messages = [{"role": "user", "content": user_message}]
            
            # Send to API
            response_text = adapter.send_message(messages)
            
            # Update usage
            self.rate_limiter.increment_usage(model_to_use)
            
            # Save to database
            conversation = Conversation(
                session_id=session_id,
                user_message=user_message,
                ai_response=response_text,
                model_used=model_to_use,
                tokens_used=0,
                created_at=datetime.now(timezone.utc)
            )
            db.session.add(conversation)
            db.session.commit()
            
            return {
                'status': 'success',
                'response': response_text,
                'model_used': model_to_use,
                'session_id': session_id,
                'warning': warning
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'response': f'Error: {str(e)}',
                'model_used': None,
                'session_id': session_id
            }
    
    def get_available_models_info(self) -> list:
        """Get info about all available models and their usage"""
        from flask import current_app
        models_config = current_app.config.get('AVAILABLE_MODELS', {})
        all_usage = self.rate_limiter.get_all_usage()
        
        models_info = []
        for provider, config in models_config.items():
            usage = all_usage.get(provider)
            models_info.append({
                'provider': provider,
                'name': config['name'],
                'usage': usage
            })
        
        return models_info