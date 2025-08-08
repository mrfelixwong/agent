"""
Unit tests for configuration system
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open
import yaml

from src.utils.config import load_config, save_config, Config, _validate_config


class TestConfigClass:
    """Test the Config class"""
    
    def test_config_init(self):
        """Test Config initialization"""
        config_dict = {'key1': 'value1', 'nested': {'key2': 'value2'}}
        config = Config(config_dict)
        assert config._config == config_dict
        
    def test_config_get_simple_key(self):
        """Test getting simple configuration key"""
        config_dict = {'key1': 'value1', 'key2': 42}
        config = Config(config_dict)
        
        assert config.get('key1') == 'value1'
        assert config.get('key2') == 42
        assert config.get('nonexistent') is None
        assert config.get('nonexistent', 'default') == 'default'
        
    def test_config_get_nested_key(self):
        """Test getting nested configuration key with dot notation"""
        config_dict = {
            'database': {
                'host': 'localhost',
                'port': 5432,
                'credentials': {
                    'username': 'admin',
                    'password': 'secret'
                }
            }
        }
        config = Config(config_dict)
        
        assert config.get('database.host') == 'localhost'
        assert config.get('database.port') == 5432
        assert config.get('database.credentials.username') == 'admin'
        assert config.get('database.nonexistent') is None
        assert config.get('database.nonexistent.key', 'default') == 'default'
        
    def test_config_getitem(self):
        """Test dictionary-style access"""
        config_dict = {'key1': 'value1'}
        config = Config(config_dict)
        
        assert config['key1'] == 'value1'
        with pytest.raises(KeyError):
            _ = config['nonexistent']
            
    def test_config_contains(self):
        """Test 'in' operator"""
        config_dict = {'key1': 'value1'}
        config = Config(config_dict)
        
        assert 'key1' in config
        assert 'nonexistent' not in config


class TestLoadConfig:
    """Test configuration loading"""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'EMAIL_ADDRESS': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password',
        'FLASK_PORT': '8080',
        'FLASK_DEBUG': 'false'
    })
    def test_load_config_from_env_only(self):
        """Test loading configuration from environment variables only"""
        with patch('os.path.exists', return_value=False):
            config = load_config()
            
        assert config['openai']['api_key'] == 'test_openai_key'
        assert config['email']['address'] == 'test@example.com'
        assert config['email']['password'] == 'test_password'
        assert config['web']['port'] == 8080
        assert config['web']['debug'] is False
        
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'EMAIL_ADDRESS': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password'
    })
    def test_load_config_with_yaml_file(self):
        """Test loading configuration with YAML file override"""
        yaml_content = {
            'web': {
                'port': 9000,
                'debug': False
            },
            'custom': {
                'setting': 'yaml_value'
            }
        }
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=yaml.dump(yaml_content))):
                config = load_config()
                
        # Environment variables should still be there
        assert config['openai']['api_key'] == 'test_openai_key'
        assert config['email']['address'] == 'test@example.com'
        
        # YAML values should override defaults
        assert config['web']['port'] == 9000
        assert config['web']['debug'] is False
        
        # Custom YAML settings should be present
        assert config['custom']['setting'] == 'yaml_value'
        
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'EMAIL_ADDRESS': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password'
    })
    def test_load_config_yaml_file_error(self):
        """Test handling of YAML file reading errors"""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', side_effect=IOError("File read error")):
                # Should not raise exception, just use defaults
                config = load_config()
                assert config['openai']['api_key'] == 'test_openai_key'
                
    def test_load_config_missing_required_keys(self):
        """Test validation of required configuration keys"""
        with patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            with patch('os.path.exists', return_value=False):
                with pytest.raises(ValueError) as exc_info:
                    load_config()
                assert "Missing required configuration keys" in str(exc_info.value)
                
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': '',  # Empty string
        'EMAIL_ADDRESS': 'test@example.com',
        'EMAIL_PASSWORD': 'test_password'
    })
    def test_load_config_empty_required_keys(self):
        """Test validation fails with empty required keys"""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(ValueError) as exc_info:
                load_config()
            assert "Missing required configuration keys" in str(exc_info.value)


class TestValidateConfig:
    """Test configuration validation"""
    
    def test_validate_config_valid(self):
        """Test validation with valid configuration"""
        config = {
            'openai': {'api_key': 'valid_key'},
            'email': {'address': 'test@example.com', 'password': 'password'}
        }
        # Should not raise exception
        _validate_config(config)
        
    def test_validate_config_missing_openai_key(self):
        """Test validation with missing OpenAI API key"""
        config = {
            'email': {'address': 'test@example.com', 'password': 'password'}
        }
        with pytest.raises(ValueError) as exc_info:
            _validate_config(config)
        assert "openai.api_key" in str(exc_info.value)
        
    def test_validate_config_missing_email_address(self):
        """Test validation with missing email address"""
        config = {
            'openai': {'api_key': 'valid_key'},
            'email': {'password': 'password'}
        }
        with pytest.raises(ValueError) as exc_info:
            _validate_config(config)
        assert "email.address" in str(exc_info.value)
        
    def test_validate_config_multiple_missing(self):
        """Test validation with multiple missing required keys"""
        config = {}
        with pytest.raises(ValueError) as exc_info:
            _validate_config(config)
        error_msg = str(exc_info.value)
        assert "openai.api_key" in error_msg
        assert "email.address" in error_msg
        assert "email.password" in error_msg


class TestSaveConfig:
    """Test configuration saving"""
    
    def test_save_config_success(self):
        """Test successful configuration saving"""
        config = {
            'openai': {'api_key': 'test_key'},
            'email': {'address': 'test@example.com'}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'test_config.yml')
            save_config(config, config_path)
            
            # Verify file was created and contains correct data
            assert os.path.exists(config_path)
            
            with open(config_path, 'r') as f:
                loaded_config = yaml.safe_load(f)
                
            assert loaded_config == config
            
    def test_save_config_creates_directory(self):
        """Test that save_config creates directory if it doesn't exist"""
        config = {'test': 'value'}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'new_dir', 'config.yml')
            save_config(config, config_path)
            
            assert os.path.exists(config_path)
            assert os.path.isdir(os.path.dirname(config_path))
            
    def test_save_config_write_error(self):
        """Test handling of write errors during save"""
        config = {'test': 'value'}
        invalid_path = '/invalid/path/config.yml'
        
        with pytest.raises(RuntimeError) as exc_info:
            save_config(config, invalid_path)
        assert "Could not save configuration" in str(exc_info.value)


# Integration test
class TestConfigIntegration:
    """Integration tests for configuration system"""
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'integration_test_key',
        'EMAIL_ADDRESS': 'integration@example.com',
        'EMAIL_PASSWORD': 'integration_password',
        'FLASK_PORT': '3000'
    })
    def test_full_config_workflow(self):
        """Test complete configuration workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'integration_config.yml')
            
            # Load initial config
            config = load_config(config_path)
            assert config['openai']['api_key'] == 'integration_test_key'
            assert config['web']['port'] == 3000
            
            # Modify and save config
            config['custom'] = {'new_setting': 'test_value'}
            save_config(config, config_path)
            
            # Load again and verify persistence
            # Need to clear environment for this test
            with patch.dict(os.environ, {
                'OPENAI_API_KEY': 'integration_test_key',
                'EMAIL_ADDRESS': 'integration@example.com',
                'EMAIL_PASSWORD': 'integration_password'
            }):
                loaded_config = load_config(config_path)
                assert loaded_config['custom']['new_setting'] == 'test_value'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])