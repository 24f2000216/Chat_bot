import os
from base_adapter import BaseAdapter
from google_adapter import GoogleGeminiAdapter
from groq_adapter import GroqAdapter
from deepseek_adapter import DeepSeekAdapter
from mistral_adapter import MistralAdapter
from openrouter_adapter import OpenRouterAdapter

class AdapterFactory:
    """Factory to create API adapters"""
    
    _adapters = {
        'google': GoogleGeminiAdapter,
        'groq': GroqAdapter,
        'deepseek': DeepSeekAdapter,
        'mistral': MistralAdapter,
        'openrouter': OpenRouterAdapter,
    }
    
    _instances = {}
    
    @classmethod
    def get_adapter(cls, provider: str) -> BaseAdapter:
        """Get or create adapter instance (singleton pattern)"""
        if provider not in cls._adapters:
            raise ValueError(f"Unknown provider: {provider}")
        
        if provider not in cls._instances:
            api_key_env_map = {
                'google': 'GOOGLE_API_KEY',
                'groq': 'GROQ_API_KEY',
                'deepseek': 'DEEPSEEK_API_KEY',
                'mistral': 'MISTRAL_API_KEY',
                'openrouter': 'OPENROUTER_API_KEY',
            }
            
            api_key = os.environ.get(api_key_env_map[provider])
            if not api_key:
                raise ValueError(f"API key not found for {provider}")
            
            adapter_class = cls._adapters[provider]
            cls._instances[provider] = adapter_class(api_key)
        
        return cls._instances[provider]
    
    @classmethod
    def get_all_providers(cls) -> list:
        """Get list of all available providers"""
        return list(cls._adapters.keys())