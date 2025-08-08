"""
Unit tests for helper utilities
"""

import os
import tempfile
import pytest
from datetime import datetime

from src.utils.helpers import (
    format_duration, safe_filename, parse_time_string, ensure_directory,
    truncate_text, validate_email, get_file_size, format_file_size
)


class TestFormatDuration:
    """Test duration formatting utility"""
    
    def test_format_duration_seconds_only(self):
        """Test formatting seconds only"""
        assert format_duration(0) == "0s"
        assert format_duration(30) == "30s"
        assert format_duration(59) == "59s"
        
    def test_format_duration_minutes_and_seconds(self):
        """Test formatting minutes and seconds"""
        assert format_duration(60) == "1m"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3599) == "59m 59s"
        
    def test_format_duration_hours_minutes_seconds(self):
        """Test formatting hours, minutes, and seconds"""
        assert format_duration(3600) == "1h"
        assert format_duration(3661) == "1h 1m 1s"
        assert format_duration(7890) == "2h 11m 30s"
        
    def test_format_duration_edge_cases(self):
        """Test edge cases for duration formatting"""
        assert format_duration(-1) == "0s"
        assert format_duration(0.5) == "0s"  # Rounds down
        assert format_duration("invalid") == "0s"
        assert format_duration(None) == "0s"


class TestSafeFilename:
    """Test safe filename utility"""
    
    def test_safe_filename_valid_name(self):
        """Test with already safe filename"""
        assert safe_filename("normal_file.txt") == "normal_file.txt"
        assert safe_filename("meeting-notes_2024.doc") == "meeting-notes_2024.doc"
        
    def test_safe_filename_invalid_characters(self):
        """Test replacing invalid characters"""
        assert safe_filename("file<>:\"/\\|?*name.txt") == "file_name.txt"
        assert safe_filename("meet:ing/notes\\file.doc") == "meet_ing_notes_file.doc"
        
    def test_safe_filename_multiple_underscores(self):
        """Test consolidating multiple underscores"""
        assert safe_filename("file___with___many___underscores") == "file_with_many_underscores"
        assert safe_filename("___leading_and_trailing___") == "leading_and_trailing"
        
    def test_safe_filename_empty_or_invalid(self):
        """Test empty or completely invalid filenames"""
        assert safe_filename("") == "unnamed"
        assert safe_filename("   ") == "unnamed"
        assert safe_filename("<>:\"/\\|?*") == "unnamed"
        assert safe_filename(None) == "unnamed"
        
    def test_safe_filename_max_length(self):
        """Test filename length limits"""
        long_name = "a" * 300
        result = safe_filename(long_name, max_length=255)
        assert len(result) <= 255
        assert result == "a" * 255
        
        # Test with invalid chars and length limit
        long_invalid = "file" + "a" * 300 + "<>invalid"
        result = safe_filename(long_invalid, max_length=10)
        assert len(result) <= 10
        assert result == "file" + "a" * 6  # "file" + 6 'a's = 10 chars


class TestParseTimeString:
    """Test time string parsing utility"""
    
    def test_parse_time_string_valid(self):
        """Test parsing valid time strings"""
        result = parse_time_string("09:30")
        assert result is not None
        assert result.hour == 9
        assert result.minute == 30
        assert result.second == 0
        
        result = parse_time_string("22:00")
        assert result is not None
        assert result.hour == 22
        assert result.minute == 0
        
        result = parse_time_string("00:00")
        assert result is not None
        assert result.hour == 0
        assert result.minute == 0
        
    def test_parse_time_string_invalid_format(self):
        """Test parsing invalid time string formats"""
        assert parse_time_string("9:30") is None  # Single digit hour
        assert parse_time_string("09:30:45") is None  # With seconds
        assert parse_time_string("09-30") is None  # Wrong separator
        assert parse_time_string("invalid") is None
        assert parse_time_string("") is None
        assert parse_time_string(None) is None
        
    def test_parse_time_string_invalid_values(self):
        """Test parsing invalid time values"""
        assert parse_time_string("25:00") is None  # Invalid hour
        assert parse_time_string("12:60") is None  # Invalid minute
        assert parse_time_string("-1:30") is None  # Negative hour
        assert parse_time_string("12:-5") is None  # Negative minute


class TestEnsureDirectory:
    """Test directory creation utility"""
    
    def test_ensure_directory_creates_new(self):
        """Test creating new directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_directory")
            assert not os.path.exists(new_dir)
            
            result = ensure_directory(new_dir)
            assert result is True
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)
            
    def test_ensure_directory_exists(self):
        """Test with existing directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = ensure_directory(temp_dir)
            assert result is True
            assert os.path.exists(temp_dir)
            
    def test_ensure_directory_nested(self):
        """Test creating nested directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = os.path.join(temp_dir, "level1", "level2", "level3")
            
            result = ensure_directory(nested_dir)
            assert result is True
            assert os.path.exists(nested_dir)
            
    def test_ensure_directory_invalid_path(self):
        """Test with invalid path (should handle gracefully)"""
        # This test might be platform-specific
        invalid_path = "/dev/null/invalid_directory"  # Can't create dir in /dev/null
        result = ensure_directory(invalid_path)
        assert result is False


class TestTruncateText:
    """Test text truncation utility"""
    
    def test_truncate_text_no_truncation_needed(self):
        """Test when no truncation is needed"""
        text = "Short text"
        assert truncate_text(text, 100) == text
        assert truncate_text(text, len(text)) == text
        
    def test_truncate_text_with_default_suffix(self):
        """Test truncation with default suffix"""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")
        assert result == "This is a very lo..."
        
    def test_truncate_text_custom_suffix(self):
        """Test truncation with custom suffix"""
        text = "Long text for testing"
        result = truncate_text(text, 15, suffix=" [more]")
        assert len(result) == 15
        assert result.endswith(" [more]")
        
    def test_truncate_text_edge_cases(self):
        """Test edge cases for text truncation"""
        assert truncate_text("", 10) == ""
        assert truncate_text(None, 10) == ""
        assert truncate_text("short", 0) == "short"  # Max length 0, but returns original


class TestValidateEmail:
    """Test email validation utility"""
    
    def test_validate_email_valid_addresses(self):
        """Test valid email addresses"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@domain.org",
            "user123@test-domain.com",
            "a@b.co"
        ]
        for email in valid_emails:
            assert validate_email(email) is True, f"Failed for {email}"
            
    def test_validate_email_invalid_addresses(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "",
            "invalid",
            "@domain.com",
            "user@",
            "user@domain",
            "user..name@domain.com",
            "user@domain..com",
            "user name@domain.com",  # Space in local part
            None,
            123  # Not a string
        ]
        for email in invalid_emails:
            assert validate_email(email) is False, f"Should have failed for {email}"


class TestGetFileSize:
    """Test file size utility"""
    
    def test_get_file_size_existing_file(self):
        """Test getting size of existing file"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            test_content = b"Hello, World!"
            temp_file.write(test_content)
            temp_file.flush()
            
            size = get_file_size(temp_file.name)
            assert size == len(test_content)
            
        # Clean up
        os.unlink(temp_file.name)
        
    def test_get_file_size_nonexistent_file(self):
        """Test getting size of non-existent file"""
        size = get_file_size("/nonexistent/file/path")
        assert size == 0
        
    def test_get_file_size_empty_file(self):
        """Test getting size of empty file"""
        with tempfile.NamedTemporaryFile() as temp_file:
            size = get_file_size(temp_file.name)
            assert size == 0


class TestFormatFileSize:
    """Test file size formatting utility"""
    
    def test_format_file_size_bytes(self):
        """Test formatting bytes"""
        assert format_file_size(0) == "0 B"
        assert format_file_size(500) == "500.0 B"
        assert format_file_size(1023) == "1023.0 B"
        
    def test_format_file_size_kilobytes(self):
        """Test formatting kilobytes"""
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1536) == "1.5 KB"  # 1.5 KB
        assert format_file_size(1048575) == "1024.0 KB"  # Almost 1 MB
        
    def test_format_file_size_megabytes(self):
        """Test formatting megabytes"""
        assert format_file_size(1048576) == "1.0 MB"  # Exactly 1 MB
        assert format_file_size(1572864) == "1.5 MB"  # 1.5 MB
        
    def test_format_file_size_gigabytes(self):
        """Test formatting gigabytes"""
        assert format_file_size(1073741824) == "1.0 GB"  # Exactly 1 GB
        assert format_file_size(1610612736) == "1.5 GB"  # 1.5 GB
        
    def test_format_file_size_terabytes(self):
        """Test formatting terabytes"""
        assert format_file_size(1099511627776) == "1.0 TB"  # Exactly 1 TB


if __name__ == '__main__':
    pytest.main([__file__, '-v'])