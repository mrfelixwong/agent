"""
Email sending system for Meeting Agent
Handles sending meeting summaries and daily reports via Gmail SMTP
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from datetime import datetime, date

from ..utils.logger import setup_logger
from ..utils.helpers import format_duration

logger = setup_logger(__name__)


class EmailSender:
    """
    Email sender for meeting summaries and daily reports
    
    Uses Gmail SMTP to send formatted email reports with meeting
    summaries, action items, and daily digest information.
    """
    
    def __init__(
        self,
        email_address: Optional[str] = None,
        email_password: Optional[str] = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587
    ):
        """
        Initialize email sender
        
        Args:
            email_address: Gmail address (optional, can use environment variable)
            email_password: Gmail app password (optional, can use environment variable)
            smtp_server: SMTP server address
            smtp_port: SMTP server port
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        
        # Set up email credentials
        self.email_address = email_address or os.getenv('EMAIL_ADDRESS')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        
        if not self.email_address:
            raise ValueError(
                "Email address required. Set EMAIL_ADDRESS environment variable or pass email_address parameter."
            )
        
        if not self.email_password:
            raise ValueError(
                "Email password required. Set EMAIL_PASSWORD environment variable or pass email_password parameter."
            )
        
        logger.info(f"Email sender initialized for: {self.email_address}")
    
    def send_meeting_summary(self, summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """
        Send individual meeting summary email
        
        Args:
            summary: Meeting summary dictionary from AI summarizer
            recipient: Email recipient (defaults to sender's email)
            
        Returns:
            True if email sent successfully
        """
        try:
            recipient = recipient or self.email_address
            
            # Create email content
            subject = self._create_meeting_subject(summary)
            html_content = self._create_meeting_html(summary)
            text_content = self._create_meeting_text(summary)
            
            # Send email
            success = self._send_email(
                recipient=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"Meeting summary sent to {recipient}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send meeting summary: {e}")
            return False
    
    def send_daily_summary(self, daily_summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """
        Send daily summary email
        
        Args:
            daily_summary: Daily summary dictionary from AI summarizer
            recipient: Email recipient (defaults to sender's email)
            
        Returns:
            True if email sent successfully
        """
        try:
            recipient = recipient or self.email_address
            
            # Create email content
            subject = self._create_daily_subject(daily_summary)
            html_content = self._create_daily_html(daily_summary)
            text_content = self._create_daily_text(daily_summary)
            
            # Send email
            success = self._send_email(
                recipient=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"Daily summary sent to {recipient}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
            return False
    
    def send_custom_email(
        self, 
        recipient: str, 
        subject: str, 
        content: str, 
        is_html: bool = False
    ) -> bool:
        """
        Send custom email
        
        Args:
            recipient: Email recipient
            subject: Email subject
            content: Email content
            is_html: Whether content is HTML formatted
            
        Returns:
            True if email sent successfully
        """
        try:
            if is_html:
                html_content = content
                text_content = self._html_to_text(content)
            else:
                html_content = self._text_to_html(content)
                text_content = content
            
            success = self._send_email(
                recipient=recipient,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if success:
                logger.info(f"Custom email sent to {recipient}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send custom email: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication
        
        Returns:
            True if connection successful
        """
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
            
            logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
    
    def _send_email(
        self, 
        recipient: str, 
        subject: str, 
        html_content: str, 
        text_content: str
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email_address
            msg["To"] = recipient
            
            # Attach text and HTML parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, recipient, msg.as_string())
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False
    
    def _create_meeting_subject(self, summary: Dict[str, Any]) -> str:
        """Create subject line for meeting summary email"""
        meeting_name = summary.get('meeting_name', 'Meeting')
        date_str = datetime.now().strftime('%Y-%m-%d')
        return f"📝 Meeting Summary: {meeting_name} - {date_str}"
    
    def _create_meeting_html(self, summary: Dict[str, Any]) -> str:
        """Create HTML content for meeting summary email"""
        meeting_name = summary.get('meeting_name', 'Meeting')
        participants = summary.get('participants', [])
        duration = summary.get('duration_minutes', 0)
        executive_summary = summary.get('executive_summary', '')
        key_points = summary.get('key_points', [])
        decisions_made = summary.get('decisions_made', [])
        action_items = summary.get('action_items', [])
        next_steps = summary.get('next_steps', [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .section {{ margin-bottom: 25px; }}
                .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
                .metadata {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 5px; }}
                .action-item {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-bottom: 10px; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📝 Meeting Summary</h1>
                <p>{meeting_name}</p>
            </div>
            
            <div class="content">
                <div class="metadata">
                    <strong>Meeting Details:</strong><br>
                    📅 Date: {datetime.now().strftime('%B %d, %Y')}<br>
                    ⏱️ Duration: {format_duration(duration * 60) if duration else 'Not recorded'}<br>
                    👥 Participants: {', '.join(participants) if participants else 'Not recorded'}
                </div>
                
                <div class="section">
                    <h2>🎯 Executive Summary</h2>
                    <p>{executive_summary or 'No executive summary available.'}</p>
                </div>
                
                <div class="section">
                    <h2>🔑 Key Points</h2>
                    {'<ul>' + ''.join(f'<li>{point}</li>' for point in key_points) + '</ul>' if key_points else '<p>No key points recorded.</p>'}
                </div>
                
                <div class="section">
                    <h2>✅ Decisions Made</h2>
                    {'<ul>' + ''.join(f'<li>{decision}</li>' for decision in decisions_made) + '</ul>' if decisions_made else '<p>No decisions recorded.</p>'}
                </div>
                
                <div class="section">
                    <h2>📋 Action Items</h2>
                    {self._format_action_items_html(action_items) if action_items else '<p>No action items recorded.</p>'}
                </div>
                
                <div class="section">
                    <h2>➡️ Next Steps</h2>
                    {'<ul>' + ''.join(f'<li>{step}</li>' for step in next_steps) + '</ul>' if next_steps else '<p>No next steps recorded.</p>'}
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by Meeting Agent on {datetime.now().strftime('%Y-%m-%d at %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_meeting_text(self, summary: Dict[str, Any]) -> str:
        """Create text content for meeting summary email"""
        meeting_name = summary.get('meeting_name', 'Meeting')
        participants = summary.get('participants', [])
        duration = summary.get('duration_minutes', 0)
        executive_summary = summary.get('executive_summary', '')
        key_points = summary.get('key_points', [])
        decisions_made = summary.get('decisions_made', [])
        action_items = summary.get('action_items', [])
        next_steps = summary.get('next_steps', [])
        
        text = f"""
📝 MEETING SUMMARY: {meeting_name}

Meeting Details:
📅 Date: {datetime.now().strftime('%B %d, %Y')}
⏱️ Duration: {format_duration(duration * 60) if duration else 'Not recorded'}
👥 Participants: {', '.join(participants) if participants else 'Not recorded'}

🎯 EXECUTIVE SUMMARY
{executive_summary or 'No executive summary available.'}

🔑 KEY POINTS
{self._format_list_text(key_points) if key_points else 'No key points recorded.'}

✅ DECISIONS MADE
{self._format_list_text(decisions_made) if decisions_made else 'No decisions recorded.'}

📋 ACTION ITEMS
{self._format_action_items_text(action_items) if action_items else 'No action items recorded.'}

➡️ NEXT STEPS
{self._format_list_text(next_steps) if next_steps else 'No next steps recorded.'}

---
Generated by Meeting Agent on {datetime.now().strftime('%Y-%m-%d at %H:%M')}
        """
        return text.strip()
    
    def _create_daily_subject(self, daily_summary: Dict[str, Any]) -> str:
        """Create subject line for daily summary email"""
        date_str = date.today().strftime('%B %d, %Y')
        total_meetings = daily_summary.get('total_meetings', 0)
        return f"📊 Daily Meeting Summary - {date_str} ({total_meetings} meetings)"
    
    def _create_daily_html(self, daily_summary: Dict[str, Any]) -> str:
        """Create HTML content for daily summary email"""
        total_meetings = daily_summary.get('total_meetings', 0)
        total_duration = daily_summary.get('total_duration', 0)
        summary_text = daily_summary.get('daily_summary', '')
        key_themes = daily_summary.get('key_themes', [])
        meeting_titles = daily_summary.get('meeting_titles', [])
        all_action_items = daily_summary.get('all_action_items', [])
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #27ae60; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .section {{ margin-bottom: 25px; }}
                .section h2 {{ color: #27ae60; border-bottom: 2px solid #2ecc71; padding-bottom: 5px; }}
                .stats {{ display: flex; justify-content: space-around; text-align: center; margin-bottom: 20px; }}
                .stat {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; flex: 1; margin: 0 10px; }}
                .stat h3 {{ color: #2c3e50; margin: 0; font-size: 24px; }}
                .stat p {{ color: #7f8c8d; margin: 5px 0 0 0; }}
                .meeting-list {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 5px; }}
                .action-item {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-bottom: 10px; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Daily Meeting Summary</h1>
                <p>{date.today().strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="content">
                <div class="stats">
                    <div class="stat">
                        <h3>{total_meetings}</h3>
                        <p>Meetings</p>
                    </div>
                    <div class="stat">
                        <h3>{format_duration(total_duration * 60) if total_duration else '0'}</h3>
                        <p>Total Time</p>
                    </div>
                    <div class="stat">
                        <h3>{len(all_action_items)}</h3>
                        <p>Action Items</p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📝 Daily Overview</h2>
                    <p>{summary_text or 'No meetings recorded today.'}</p>
                </div>
                
                <div class="section">
                    <h2>🎯 Key Themes</h2>
                    {'<ul>' + ''.join(f'<li>{theme}</li>' for theme in key_themes) + '</ul>' if key_themes else '<p>No key themes identified.</p>'}
                </div>
                
                <div class="section">
                    <h2>📅 Today\'s Meetings</h2>
                    <div class="meeting-list">
                        {'<ul>' + ''.join(f'<li>{title}</li>' for title in meeting_titles) + '</ul>' if meeting_titles else '<p>No meetings recorded.</p>'}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 All Action Items</h2>
                    {self._format_action_items_html(all_action_items) if all_action_items else '<p>No action items recorded today.</p>'}
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by Meeting Agent on {datetime.now().strftime('%Y-%m-%d at %H:%M')}</p>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_daily_text(self, daily_summary: Dict[str, Any]) -> str:
        """Create text content for daily summary email"""
        total_meetings = daily_summary.get('total_meetings', 0)
        total_duration = daily_summary.get('total_duration', 0)
        summary_text = daily_summary.get('daily_summary', '')
        key_themes = daily_summary.get('key_themes', [])
        meeting_titles = daily_summary.get('meeting_titles', [])
        all_action_items = daily_summary.get('all_action_items', [])
        
        text = f"""
📊 DAILY MEETING SUMMARY - {date.today().strftime('%B %d, %Y')}

STATISTICS
📅 Total Meetings: {total_meetings}
⏱️ Total Time: {format_duration(total_duration * 60) if total_duration else '0'}
📋 Action Items: {len(all_action_items)}

📝 DAILY OVERVIEW
{summary_text or 'No meetings recorded today.'}

🎯 KEY THEMES
{self._format_list_text(key_themes) if key_themes else 'No key themes identified.'}

📅 TODAY'S MEETINGS
{self._format_list_text(meeting_titles) if meeting_titles else 'No meetings recorded.'}

📋 ALL ACTION ITEMS
{self._format_action_items_text(all_action_items) if all_action_items else 'No action items recorded today.'}

---
Generated by Meeting Agent on {datetime.now().strftime('%Y-%m-%d at %H:%M')}
        """
        return text.strip()
    
    def _format_action_items_html(self, action_items: List[Dict[str, Any]]) -> str:
        """Format action items as HTML"""
        if not action_items:
            return ""
        
        html_items = []
        for item in action_items:
            if isinstance(item, dict):
                task = item.get('task', str(item))
                assignee = item.get('assignee', 'Not assigned')
                deadline = item.get('deadline', 'No deadline')
                priority = item.get('priority', 'medium')
                
                html_items.append(f"""
                <div class="action-item">
                    <strong>{task}</strong><br>
                    👤 Assignee: {assignee}<br>
                    📅 Deadline: {deadline}<br>
                    🔥 Priority: {priority.capitalize()}
                </div>
                """)
            else:
                html_items.append(f'<div class="action-item">{str(item)}</div>')
        
        return ''.join(html_items)
    
    def _format_action_items_text(self, action_items: List[Dict[str, Any]]) -> str:
        """Format action items as text"""
        if not action_items:
            return ""
        
        text_items = []
        for i, item in enumerate(action_items, 1):
            if isinstance(item, dict):
                task = item.get('task', str(item))
                assignee = item.get('assignee', 'Not assigned')
                deadline = item.get('deadline', 'No deadline')
                priority = item.get('priority', 'medium')
                
                text_items.append(f"""
{i}. {task}
   👤 Assignee: {assignee}
   📅 Deadline: {deadline}
   🔥 Priority: {priority.capitalize()}
                """.strip())
            else:
                text_items.append(f"{i}. {str(item)}")
        
        return '\n\n'.join(text_items)
    
    def _format_list_text(self, items: List[str]) -> str:
        """Format list items as text"""
        return '\n'.join(f"• {item}" for item in items)
    
    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text (simple implementation)"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        return text.strip()
    
    def _text_to_html(self, text: str) -> str:
        """Convert plain text to HTML"""
        # Escape HTML characters
        html = text.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        # Convert line breaks to <br>
        html = html.replace('\n', '<br>')
        return f"<html><body><pre>{html}</pre></body></html>"


class MockEmailSender(EmailSender):
    """
    Mock email sender for testing without actual email sending
    """
    
    def __init__(self, **kwargs):
        """Initialize mock email sender"""
        # Don't call parent __init__ to avoid email credential validation
        self.smtp_server = kwargs.get('smtp_server', 'mock.smtp.server')
        self.smtp_port = kwargs.get('smtp_port', 587)
        self.email_address = kwargs.get('email_address', 'test@example.com')
        self.email_password = kwargs.get('email_password', 'mock_password')
        
        # Mock settings
        self._simulate_error = False
        self._sent_emails = []  # Track sent emails for testing
        
    def set_simulate_error(self, should_error: bool):
        """Set whether to simulate email sending errors"""
        self._simulate_error = should_error
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get list of sent emails for testing verification"""
        return self._sent_emails.copy()
    
    def clear_sent_emails(self):
        """Clear sent emails list"""
        self._sent_emails.clear()
    
    def send_meeting_summary(self, summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Mock send meeting summary"""
        if self._simulate_error:
            return False
        
        recipient = recipient or self.email_address
        
        # Create mock email record
        email_record = {
            'type': 'meeting_summary',
            'recipient': recipient,
            'subject': self._create_meeting_subject(summary),
            'meeting_name': summary.get('meeting_name'),
            'sent_at': datetime.now().isoformat()
        }
        self._sent_emails.append(email_record)
        
        return True
    
    def send_daily_summary(self, daily_summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Mock send daily summary"""
        if self._simulate_error:
            return False
        
        recipient = recipient or self.email_address
        
        # Create mock email record
        email_record = {
            'type': 'daily_summary',
            'recipient': recipient,
            'subject': self._create_daily_subject(daily_summary),
            'total_meetings': daily_summary.get('total_meetings', 0),
            'sent_at': datetime.now().isoformat()
        }
        self._sent_emails.append(email_record)
        
        return True
    
    def send_custom_email(
        self, 
        recipient: str, 
        subject: str, 
        content: str, 
        is_html: bool = False
    ) -> bool:
        """Mock send custom email"""
        if self._simulate_error:
            return False
        
        # Create mock email record
        email_record = {
            'type': 'custom',
            'recipient': recipient,
            'subject': subject,
            'content_length': len(content),
            'is_html': is_html,
            'sent_at': datetime.now().isoformat()
        }
        self._sent_emails.append(email_record)
        
        return True
    
    def test_connection(self) -> bool:
        """Mock test connection"""
        return not self._simulate_error