"""
Configuration management for Meeting Agent
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Meeting Agent"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self._config = config_dict
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
        
    def __getitem__(self, key: str) -> Any:
        return self._config[key]
        
    def __contains__(self, key: str) -> bool:
        return key in self._config

def load_config(config_path: Optional[str] = None, validate_secrets: bool = True) -> Dict[str, Any]:
    """
    Load configuration using hybrid approach:
    - Non-sensitive settings from YAML file
    - Secrets from environment variables
    
    Args:
        config_path: Path to YAML config file
        validate_secrets: Whether to validate required secrets (False for mock components)
    """
    
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.yml"
    
    # Start with default configuration
    config = {}
    
    # Load settings from YAML file first
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
    
    # Add secrets from environment variables
    # These override any values from the YAML file for security
    
    # OpenAI secrets
    if 'openai' not in config:
        config['openai'] = {}
    config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
    
    # Email secrets
    if 'email' not in config:
        config['email'] = {}
    config['email']['address'] = os.getenv('EMAIL_ADDRESS')
    config['email']['password'] = os.getenv('EMAIL_PASSWORD')
    
    # Web secrets
    if 'web' not in config:
        config['web'] = {}
    # Only override secret_key from environment, keep other web settings from YAML
    if os.getenv('SECRET_KEY'):
        config['web']['secret_key'] = os.getenv('SECRET_KEY')
    elif 'secret_key' not in config.get('web', {}):
        config['web']['secret_key'] = 'default-secret-key'
    
    # Validate required configuration (skip for mock components)
    if validate_secrets:
        _validate_config(config)
    
    return config

def _validate_config(config: Dict[str, Any]) -> None:
    """Validate that required configuration values are present"""
    required_secrets = [
        ('openai.api_key', 'OPENAI_API_KEY'),
        ('email.address', 'EMAIL_ADDRESS'), 
        ('email.password', 'EMAIL_PASSWORD')
    ]
    
    missing_secrets = []
    for config_key, env_var in required_secrets:
        keys = config_key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
        if not value:
            missing_secrets.append(f"{config_key} (set {env_var} environment variable)")
    
    if missing_secrets:
        raise ValueError(f"Missing required secrets: {', '.join(missing_secrets)}")

def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """Save configuration to YAML file"""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.yml"
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    try:
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    except Exception as e:
        raise RuntimeError(f"Could not save configuration to {config_path}: {e}")