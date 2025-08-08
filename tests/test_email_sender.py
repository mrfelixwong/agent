"""
Unit tests for email sending system
"""

import os
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime

# Import the components we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.notifications.sender import EmailSender, MockEmailSender


class TestMockEmailSender:
    """Test MockEmailSender (no SMTP dependencies)"""
    
    def test_mock_sender_initialization(self):
        """Test mock email sender initialization"""
        sender = MockEmailSender(
            email_address="custom@example.com",
            smtp_server="custom.smtp.com",
            smtp_port=465
        )
        
        assert sender.email_address == "custom@example.com"
        assert sender.smtp_server == "custom.smtp.com"
        assert sender.smtp_port == 465
        
    def test_mock_sender_default_initialization(self):
        """Test mock email sender with default values"""
        sender = MockEmailSender()
        
        assert sender.email_address == "test@example.com"
        assert sender.smtp_server == "mock.smtp.server"
        assert sender.smtp_port == 587
        
    def test_mock_meeting_summary_email(self):
        """Test mock meeting summary email sending"""
        sender = MockEmailSender()
        
        summary = {
            'meeting_name': 'Test Meeting',
            'participants': ['Alice', 'Bob'],
            'duration_minutes': 30,
            'executive_summary': 'This was a productive meeting about project planning.',
            'key_points': ['Discussed timeline', 'Reviewed budget'],
            'decisions_made': ['Approved budget increase'],
            'action_items': [
                {'task': 'Update timeline', 'assignee': 'Alice', 'deadline': 'Friday', 'priority': 'high'}
            ],
            'next_steps': ['Schedule follow-up meeting']
        }
        
        success = sender.send_meeting_summary(summary, "recipient@example.com")
        assert success is True
        
        # Check sent emails
        sent_emails = sender.get_sent_emails()
        assert len(sent_emails) == 1
        
        email = sent_emails[0]
        assert email['type'] == 'meeting_summary'
        assert email['recipient'] == "recipient@example.com"
        assert email['meeting_name'] == 'Test Meeting'
        assert '📝 Meeting Summary: Test Meeting' in email['subject']
        
    def test_mock_daily_summary_email(self):
        """Test mock daily summary email sending"""
        sender = MockEmailSender()
        
        daily_summary = {
            'total_meetings': 3,
            'total_duration': 120,
            'daily_summary': 'Today was productive with 3 meetings covering various topics.',
            'key_themes': ['Project Planning', 'Budget Review'],
            'meeting_titles': ['Morning Standup', 'Client Call', 'Team Review'],
            'all_action_items': [
                {'task': 'Task 1', 'assignee': 'John'},
                {'task': 'Task 2', 'assignee': 'Sarah'}
            ]
        }
        
        success = sender.send_daily_summary(daily_summary)
        assert success is True
        
        # Check sent emails
        sent_emails = sender.get_sent_emails()
        assert len(sent_emails) == 1
        
        email = sent_emails[0]
        assert email['type'] == 'daily_summary'
        assert email['recipient'] == "test@example.com"  # Default recipient
        assert email['total_meetings'] == 3
        assert '📊 Daily Meeting Summary' in email['subject']
        assert '(3 meetings)' in email['subject']
        
    def test_mock_custom_email(self):
        """Test mock custom email sending"""
        sender = MockEmailSender()
        
        success = sender.send_custom_email(
            recipient="custom@example.com",
            subject="Test Custom Email",
            content="<h1>This is a test email</h1>",
            is_html=True
        )
        assert success is True
        
        # Check sent emails
        sent_emails = sender.get_sent_emails()
        assert len(sent_emails) == 1
        
        email = sent_emails[0]
        assert email['type'] == 'custom'
        assert email['recipient'] == "custom@example.com"
        assert email['subject'] == "Test Custom Email"
        assert email['is_html'] is True
        assert email['content_length'] > 0
        
    def test_mock_connection_test(self):
        """Test mock connection testing"""
        sender = MockEmailSender()
        
        # Should succeed by default
        assert sender.test_connection() is True
        
        # Should fail when error is simulated
        sender.set_simulate_error(True)
        assert sender.test_connection() is False
        
    def test_mock_error_simulation(self):
        """Test mock error simulation"""
        sender = MockEmailSender()
        sender.set_simulate_error(True)
        
        summary = {'meeting_name': 'Test Meeting'}
        daily_summary = {'total_meetings': 1}
        
        # All email sending should fail
        assert sender.send_meeting_summary(summary) is False
        assert sender.send_daily_summary(daily_summary) is False
        assert sender.send_custom_email("test@example.com", "Subject", "Content") is False
        
        # No emails should be recorded
        assert len(sender.get_sent_emails()) == 0
        
    def test_mock_email_tracking(self):
        """Test mock email tracking functionality"""
        sender = MockEmailSender()
        
        # Send multiple emails
        sender.send_meeting_summary({'meeting_name': 'Meeting 1'})
        sender.send_daily_summary({'total_meetings': 2})
        sender.send_custom_email("test@example.com", "Custom", "Content")
        
        # Check all emails were tracked
        sent_emails = sender.get_sent_emails()
        assert len(sent_emails) == 3
        
        email_types = [email['type'] for email in sent_emails]
        assert 'meeting_summary' in email_types
        assert 'daily_summary' in email_types
        assert 'custom' in email_types
        
        # Test clearing emails
        sender.clear_sent_emails()
        assert len(sender.get_sent_emails()) == 0
        
    def test_mock_email_metadata(self):
        """Test mock email metadata tracking"""
        sender = MockEmailSender()
        
        before_time = datetime.now()
        sender.send_meeting_summary({'meeting_name': 'Test Meeting'})
        after_time = datetime.now()
        
        sent_emails = sender.get_sent_emails()
        email = sent_emails[0]
        
        # Check timestamp
        sent_time = datetime.fromisoformat(email['sent_at'])
        assert before_time <= sent_time <= after_time
        
        # Check all required fields are present
        required_fields = ['type', 'recipient', 'subject', 'sent_at']
        for field in required_fields:
            assert field in email


class TestEmailSenderWithMocks:
    """Test EmailSender with mocked SMTP"""
    
    def test_sender_init_missing_credentials(self):
        """Test EmailSender initialization with missing credentials"""
        with patch.dict(os.environ, {}, clear=True):
            try:
                EmailSender()
                assert False, "Should have raised ValueError for missing email"
            except ValueError as e:
                assert "Email address required" in str(e)
                
            try:
                EmailSender(email_address="test@example.com")
                assert False, "Should have raised ValueError for missing password"
            except ValueError as e:
                assert "Email password required" in str(e)
                
    def test_sender_successful_init(self):
        """Test successful EmailSender initialization"""
        sender = EmailSender(
            email_address="test@example.com",
            email_password="test_password",
            smtp_server="smtp.test.com",
            smtp_port=465
        )
        
        assert sender.email_address == "test@example.com"
        assert sender.email_password == "test_password"
        assert sender.smtp_server == "smtp.test.com"
        assert sender.smtp_port == 465
        
    def test_sender_with_env_credentials(self):
        """Test EmailSender initialization with environment credentials"""
        with patch.dict(os.environ, {
            'EMAIL_ADDRESS': 'env_test@example.com',
            'EMAIL_PASSWORD': 'env_test_password'
        }):
            sender = EmailSender()
            
            assert sender.email_address == 'env_test@example.com'
            assert sender.email_password == 'env_test_password'
            
    def test_mocked_smtp_connection(self):
        """Test SMTP connection with mocked server"""
        sender = EmailSender(
            email_address="test@example.com",
            email_password="test_password"
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            success = sender.test_connection()
            assert success is True
            
            # Verify SMTP calls
            mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@example.com", "test_password")
            
    def test_mocked_smtp_connection_failure(self):
        """Test SMTP connection failure handling"""
        sender = EmailSender(
            email_address="test@example.com",
            email_password="wrong_password"
        )
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.return_value.__enter__.return_value.login.side_effect = Exception("Authentication failed")
            
            success = sender.test_connection()
            assert success is False
            
    def test_mocked_email_sending(self):
        """Test email sending with mocked SMTP"""
        sender = EmailSender(
            email_address="sender@example.com",
            email_password="password"
        )
        
        summary = {
            'meeting_name': 'Test Meeting',
            'participants': ['Alice', 'Bob'],
            'duration_minutes': 45,
            'executive_summary': 'Productive meeting about project planning.',
            'key_points': ['Timeline discussed', 'Budget approved'],
            'decisions_made': ['Move forward with plan'],
            'action_items': [
                {'task': 'Create timeline', 'assignee': 'Alice', 'deadline': 'Next week', 'priority': 'high'}
            ],
            'next_steps': ['Schedule follow-up']
        }
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            success = sender.send_meeting_summary(summary, "recipient@example.com")
            assert success is True
            
            # Verify email was sent
            mock_server.sendmail.assert_called_once()
            call_args = mock_server.sendmail.call_args[0]
            assert call_args[0] == "sender@example.com"
            assert call_args[1] == "recipient@example.com"
            assert "Meeting Summary: Test Meeting" in call_args[2]


class TestEmailContentFormatting:
    """Test email content formatting"""
    
    def test_meeting_summary_html_formatting(self):
        """Test HTML formatting for meeting summary"""
        sender = MockEmailSender()
        
        summary = {
            'meeting_name': 'Project Planning Session',
            'participants': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'duration_minutes': 75,
            'executive_summary': 'Comprehensive review of Q4 project deliverables and timeline adjustments.',
            'key_points': [
                'Reviewed current milestone progress',
                'Discussed resource allocation challenges',
                'Identified critical path dependencies'
            ],
            'decisions_made': [
                'Approved additional budget for contractor support',
                'Extended deadline by 2 weeks for testing phase'
            ],
            'action_items': [
                {
                    'task': 'Update project timeline with new milestones',
                    'assignee': 'John Doe',
                    'deadline': 'End of week',
                    'priority': 'high'
                },
                {
                    'task': 'Negotiate contractor rates',
                    'assignee': 'Jane Smith',
                    'deadline': 'Next Tuesday',
                    'priority': 'medium'
                }
            ],
            'next_steps': [
                'Schedule weekly project reviews',
                'Set up contractor onboarding process'
            ]
        }
        
        html_content = sender._create_meeting_html(summary)
        
        # Check HTML structure and content
        assert '<html>' in html_content
        assert '<body>' in html_content
        assert 'Project Planning Session' in html_content
        assert 'John Doe, Jane Smith, Bob Johnson' in html_content
        assert '1h 15m' in html_content  # Duration formatting
        assert 'Comprehensive review of Q4' in html_content
        assert 'Update project timeline' in html_content
        assert 'high' in html_content.lower()  # Priority
        
    def test_meeting_summary_text_formatting(self):
        """Test text formatting for meeting summary"""
        sender = MockEmailSender()
        
        summary = {
            'meeting_name': 'Budget Review',
            'participants': ['CFO', 'PM', 'Dev Lead'],
            'duration_minutes': 30,
            'executive_summary': 'Quarterly budget review and allocation decisions.',
            'key_points': ['Q3 spending analysis', 'Q4 budget planning'],
            'decisions_made': ['Approved tool upgrades'],
            'action_items': [
                {'task': 'Purchase licenses', 'assignee': 'PM', 'deadline': 'ASAP', 'priority': 'high'}
            ],
            'next_steps': ['Monthly budget tracking']
        }
        
        text_content = sender._create_meeting_text(summary)
        
        # Check text structure and content
        assert '📝 MEETING SUMMARY: Budget Review' in text_content
        assert 'CFO, PM, Dev Lead' in text_content
        assert '30s' in text_content or '0h 0m 30s' in text_content  # Duration
        assert '🎯 EXECUTIVE SUMMARY' in text_content
        assert 'Quarterly budget review' in text_content
        assert '📋 ACTION ITEMS' in text_content
        assert 'Purchase licenses' in text_content
        
    def test_daily_summary_formatting(self):
        """Test daily summary formatting"""
        sender = MockEmailSender()
        
        daily_summary = {
            'total_meetings': 4,
            'total_duration': 180,  # 3 hours
            'daily_summary': 'Highly productive day with strategic planning sessions and client reviews.',
            'key_themes': ['Strategic Planning', 'Client Relations', 'Product Development'],
            'meeting_titles': [
                'Morning Standup',
                'Client Check-in',
                'Product Strategy Session',
                'Team Retrospective'
            ],
            'all_action_items': [
                {'task': 'Update roadmap', 'assignee': 'Product Manager'},
                {'task': 'Follow up with client', 'assignee': 'Account Manager'},
                {'task': 'Schedule user interviews', 'assignee': 'UX Designer'}
            ]
        }
        
        html_content = sender._create_daily_html(daily_summary)
        text_content = sender._create_daily_text(daily_summary)
        
        # Check HTML content
        assert '📊 Daily Meeting Summary' in html_content
        assert '<h3>4</h3>' in html_content  # Meeting count
        assert '3h' in html_content  # Duration formatting
        assert 'Strategic Planning' in html_content
        assert 'Update roadmap' in html_content
        
        # Check text content
        assert '📊 DAILY MEETING SUMMARY' in text_content
        assert 'Total Meetings: 4' in text_content
        assert '3h' in text_content
        assert 'Strategic Planning' in text_content
        assert 'Update roadmap' in text_content
        
    def test_action_items_formatting(self):
        """Test action items formatting in various scenarios"""
        sender = MockEmailSender()
        
        # Test with structured action items
        structured_items = [
            {
                'task': 'Review proposal document',
                'assignee': 'John Smith',
                'deadline': '2024-01-15',
                'priority': 'high'
            },
            {
                'task': 'Schedule client meeting',
                'assignee': 'Sarah Johnson',
                'deadline': 'Next week',
                'priority': 'medium'
            }
        ]
        
        html_formatted = sender._format_action_items_html(structured_items)
        text_formatted = sender._format_action_items_text(structured_items)
        
        # Check HTML formatting
        assert 'Review proposal document' in html_formatted
        assert 'John Smith' in html_formatted
        assert '2024-01-15' in html_formatted
        assert 'High' in html_formatted  # Capitalized priority
        
        # Check text formatting
        assert '1. Review proposal document' in text_formatted
        assert '👤 Assignee: John Smith' in text_formatted
        assert '📅 Deadline: 2024-01-15' in text_formatted
        assert '🔥 Priority: High' in text_formatted
        
        # Test with simple string action items
        simple_items = ["Complete user testing", "Update documentation"]
        
        html_simple = sender._format_action_items_html(simple_items)
        text_simple = sender._format_action_items_text(simple_items)
        
        assert 'Complete user testing' in html_simple
        assert '1. Complete user testing' in text_simple
        assert '2. Update documentation' in text_simple
        
    def test_subject_line_generation(self):
        """Test email subject line generation"""
        sender = MockEmailSender()
        
        # Test meeting summary subject
        summary = {'meeting_name': 'Weekly Team Sync'}
        subject = sender._create_meeting_subject(summary)
        
        assert '📝 Meeting Summary:' in subject
        assert 'Weekly Team Sync' in subject
        assert datetime.now().strftime('%Y-%m-%d') in subject
        
        # Test daily summary subject
        daily_summary = {'total_meetings': 5}
        daily_subject = sender._create_daily_subject(daily_summary)
        
        assert '📊 Daily Meeting Summary' in daily_subject
        assert '(5 meetings)' in daily_subject
        assert datetime.now().strftime('%B %d, %Y') in daily_subject


def run_email_tests():
    """Run all email sender tests"""
    print("📧 Testing Email System...")
    
    test_classes = [
        TestMockEmailSender,
        TestEmailSenderWithMocks,
        TestEmailContentFormatting
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n  Testing {class_name}:")
        
        instance = test_class()
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                getattr(instance, test_method)()
                print(f"    ✅ {test_method}")
                passed_tests += 1
            except Exception as e:
                print(f"    ❌ {test_method}: {e}")
    
    print(f"\n📊 Email Tests: {passed_tests}/{total_tests} passed")
    return passed_tests == total_tests


if __name__ == '__main__':
    success = run_email_tests()
    exit(0 if success else 1)