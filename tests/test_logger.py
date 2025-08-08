"""
Unit tests for logging utilities
"""

import os
import logging
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

from src.utils.logger import setup_logger, get_logger


class TestSetupLogger:
    """Test logger setup utility"""
    
    def test_setup_logger_basic(self):
        """Test basic logger setup"""
        logger = setup_logger("test_logger")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1  # At least console handler
        
    def test_setup_logger_custom_level(self):
        """Test logger setup with custom level"""
        logger = setup_logger("test_logger_debug", level="DEBUG")
        assert logger.level == logging.DEBUG
        
        logger = setup_logger("test_logger_error", level="ERROR")
        assert logger.level == logging.ERROR
        
        # Test invalid level (should default to INFO)
        logger = setup_logger("test_logger_invalid", level="INVALID")
        assert logger.level == logging.INFO
        
    def test_setup_logger_with_file(self):
        """Test logger setup with file handler"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            logger = setup_logger("test_file_logger", log_file=log_file)
            
            # Should have console + file handlers
            assert len(logger.handlers) == 2
            
            # Test that log file directory was created
            assert os.path.exists(log_file)
            
    def test_setup_logger_file_in_nested_directory(self):
        """Test logger setup with file in nested directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "nested", "dir", "test.log")
            logger = setup_logger("test_nested_logger", log_file=log_file)
            
            # Directory should be created
            assert os.path.exists(os.path.dirname(log_file))
            assert len(logger.handlers) == 2
            
    def test_setup_logger_no_duplicate_handlers(self):
        """Test that setting up same logger twice doesn't duplicate handlers"""
        logger1 = setup_logger("duplicate_test")
        initial_handler_count = len(logger1.handlers)
        
        logger2 = setup_logger("duplicate_test")  # Same name
        
        # Should be same logger instance
        assert logger1 is logger2
        # Should not have duplicate handlers
        assert len(logger2.handlers) == initial_handler_count
        
    def test_setup_logger_formatting(self):
        """Test logger message formatting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "format_test.log")
            logger = setup_logger("format_test_logger", log_file=log_file)
            
            test_message = "Test log message"
            logger.info(test_message)
            
            # Read the log file and check format
            with open(log_file, 'r') as f:
                log_content = f.read()
                
            assert test_message in log_content
            assert "format_test_logger" in log_content
            assert "INFO" in log_content
            # Should contain timestamp (basic check)
            assert any(char.isdigit() for char in log_content)


class TestGetLogger:
    """Test get_logger utility"""
    
    def test_get_logger_existing(self):
        """Test getting existing logger"""
        # First create a logger
        original_logger = setup_logger("existing_logger_test")
        
        # Then get it
        retrieved_logger = get_logger("existing_logger_test")
        
        assert retrieved_logger is original_logger
        assert retrieved_logger.name == "existing_logger_test"
        
    def test_get_logger_nonexistent(self):
        """Test getting non-existent logger"""
        logger = get_logger("nonexistent_logger")
        
        # Should return a logger, but without handlers
        assert isinstance(logger, logging.Logger)
        assert logger.name == "nonexistent_logger"
        # Default logger from logging.getLogger won't have our custom handlers
        

class TestLoggerIntegration:
    """Integration tests for logging system"""
    
    def test_logger_file_rotation(self):
        """Test that file handler uses rotation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "rotation_test.log")
            logger = setup_logger("rotation_test_logger", log_file=log_file)
            
            # Find the RotatingFileHandler
            file_handler = None
            for handler in logger.handlers:
                if hasattr(handler, 'maxBytes'):  # RotatingFileHandler
                    file_handler = handler
                    break
                    
            assert file_handler is not None
            assert file_handler.maxBytes == 10 * 1024 * 1024  # 10MB
            assert file_handler.backupCount == 5
            
    def test_logger_console_output(self, capfd):
        """Test logger console output"""
        logger = setup_logger("console_test_logger")
        
        test_message = "Console test message"
        logger.info(test_message)
        
        captured = capfd.readouterr()
        assert test_message in captured.out
        assert "INFO" in captured.out
        
    def test_logger_different_levels(self, capfd):
        """Test logging at different levels"""
        logger = setup_logger("level_test_logger", level="DEBUG")
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "Debug message" in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output
        
    def test_logger_level_filtering(self, capfd):
        """Test that lower level messages are filtered out"""
        logger = setup_logger("filter_test_logger", level="WARNING")
        
        logger.debug("This should not appear")
        logger.info("This should not appear either")
        logger.warning("This should appear")
        logger.error("This should also appear")
        
        captured = capfd.readouterr()
        output = captured.out
        
        assert "This should not appear" not in output
        assert "This should appear" in output
        assert "This should also appear" in output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])