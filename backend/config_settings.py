import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost/ai_chat_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JSON_SORT_KEYS = False
    
    # API Keys (set in .env file)
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
    
    # Rate limit warnings
    USAGE_WARNING_THRESHOLD = 0.80  # Warn at 80%
    
    # Available models config
    AVAILABLE_MODELS = {
        'google': {
            'name': 'Google Gemini 3.7 Flash',
            'model_id': 'gemini-1.5-flash',
            'daily_limit': 1500,
            'provider': 'google',
            'is_active': True,
            'api_key_env': 'GOOGLE_API_KEY'
        },
        'groq': {
            'name': 'Groq GPT-OSS 120B',
            'model_id': 'mixtral-8x7b-32768',
            'daily_limit': 1000,
            'provider': 'groq',
            'is_active': True,
            'api_key_env': 'GROQ_API_KEY'
        },
        'openrouter': {
            'name': 'OpenRouter GPT-OSS 120B',
            'model_id': 'openrouter/gpt-oss-120b',
            'daily_limit': 999999,  # Effectively unlimited for free
            'provider': 'openrouter',
            'is_active': True,
            'api_key_env': 'OPENROUTER_API_KEY'
        },
        'deepseek': {
            'name': 'DeepSeek V4 Flash',
            'model_id': 'deepseek-chat',
            'daily_limit': 2000,
            'provider': 'deepseek',
            'is_active': True,
            'api_key_env': 'DEEPSEEK_API_KEY'
        },
        'mistral': {
            'name': 'Mistral Small 3.1',
            'model_id': 'mistral-small-latest',
            'daily_limit': 1200,
            'provider': 'mistral',
            'is_active': True,
            'api_key_env': 'MISTRAL_API_KEY'
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'