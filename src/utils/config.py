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

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file and environment variables"""
    
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.yml"
    
    # Default configuration
    config = {
        'openai': {
            'api_key': os.getenv('OPENAI_API_KEY'),
        },
        'email': {
            'address': os.getenv('EMAIL_ADDRESS'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'daily_summary_time': os.getenv('DAILY_SUMMARY_TIME', '22:00')
        },
        'web': {
            'host': os.getenv('WEB_HOST', 'localhost'),
            'port': int(os.getenv('WEB_PORT', '5002')),
            'secret_key': os.getenv('SECRET_KEY', 'default-secret'),
            'debug': os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        },
        'database': {
            'url': os.getenv('DATABASE_URL', 'sqlite:///data/database.db')
        },
        'audio': {
            'sample_rate': int(os.getenv('AUDIO_SAMPLE_RATE', '44100')),
            'channels': int(os.getenv('AUDIO_CHANNELS', '2')),
            'format': os.getenv('AUDIO_FORMAT', '16bit')
        },
        'logging': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'file': os.getenv('LOG_FILE', 'logs/meeting_agent.log')
        }
    }
    
    # Load from YAML file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    config.update(yaml_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
    
    # Validate required configuration
    _validate_config(config)
    
    return config

def _validate_config(config: Dict[str, Any]) -> None:
    """Validate that required configuration values are present"""
    required_keys = [
        'openai.api_key',
        'email.address',
        'email.password'
    ]
    
    missing_keys = []
    for key in required_keys:
        keys = key.split('.')
        value = config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
        if not value:
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

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