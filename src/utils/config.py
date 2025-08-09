"""Configuration management for Meeting Agent"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    keys = key.split('.')
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    return value

def load_config(config_path: Optional[str] = None, validate_secrets: bool = True) -> Dict[str, Any]:
    """Load configuration from YAML file and environment variables"""
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.yml"
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception:
            pass  # Config file is optional
    if 'openai' not in config:
        config['openai'] = {}
    config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
    if 'email' not in config:
        config['email'] = {}
    config['email']['address'] = os.getenv('EMAIL_ADDRESS')
    config['email']['password'] = os.getenv('EMAIL_PASSWORD')
    if 'web' not in config:
        config['web'] = {}
    if os.getenv('SECRET_KEY'):
        config['web']['secret_key'] = os.getenv('SECRET_KEY')
    elif 'secret_key' not in config.get('web', {}):
        config['web']['secret_key'] = 'default-secret-key'
    if validate_secrets:
        _validate_config(config)
    return config

def _validate_config(config: Dict[str, Any]) -> None:
    required_secrets = [
        ('openai.api_key', 'OPENAI_API_KEY'),
    ]
    missing_secrets = []
    for config_key, env_var in required_secrets:
        if not get_config_value(config, config_key):
            missing_secrets.append(f"{config_key} (set {env_var} environment variable)")
    if missing_secrets:
        raise ValueError(f"Missing required secrets: {', '.join(missing_secrets)}")