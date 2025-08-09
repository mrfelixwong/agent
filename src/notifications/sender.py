"""
Simple email sender for Meeting Agent
Sends plain text email notifications for meetings
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailSender:
    """Simple email sender for meeting notifications"""
    
    def __init__(
        self,
        email_address: Optional[str] = None,
        email_password: Optional[str] = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587
    ):
        """Initialize email sender with credentials"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = email_address or os.getenv('EMAIL_ADDRESS')
        self.email_password = email_password or os.getenv('EMAIL_PASSWORD')
        
        if not self.email_address or not self.email_password:
            logger.warning("Email credentials not configured - email features disabled")
    
    def send_meeting_summary(self, summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Send meeting summary email"""
        if not self.email_address or not self.email_password:
            return False
            
        try:
            recipient = recipient or self.email_address
            subject = f"Meeting Summary: {summary.get('meeting_name', 'Unknown')}"
            
            # Create simple text content
            content = self._format_meeting_summary(summary)
            
            return self._send_email(recipient, subject, content)
            
        except Exception as e:
            logger.error(f"Failed to send meeting summary: {e}")
            return False
    
    def send_daily_summary(self, daily_summary: Dict[str, Any], recipient: Optional[str] = None) -> bool:
        """Send daily summary email"""
        if not self.email_address or not self.email_password:
            return False
            
        try:
            recipient = recipient or self.email_address
            total_meetings = daily_summary.get('total_meetings', 0)
            subject = f"Daily Summary - {total_meetings} meetings"
            
            # Create simple text content
            content = self._format_daily_summary(daily_summary)
            
            return self._send_email(recipient, subject, content)
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {e}")
            return False
    
    def _send_email(self, recipient: str, subject: str, content: str) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEText(content)
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = recipient
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
    
    def _format_meeting_summary(self, summary: Dict[str, Any]) -> str:
        """Format meeting summary as plain text"""
        lines = [
            f"MEETING SUMMARY: {summary.get('meeting_name', 'Unknown')}",
            f"Date: {datetime.now().strftime('%B %d, %Y')}",
            f"Duration: {summary.get('duration_minutes', 0)} minutes",
            "",
            "EXECUTIVE SUMMARY:",
            summary.get('executive_summary', 'No summary available'),
            "",
            "KEY POINTS:",
        ]
        
        for point in summary.get('key_points', []):
            lines.append(f"• {point}")
        
        lines.extend(["", "DECISIONS:"])
        for decision in summary.get('decisions_made', []):
            lines.append(f"• {decision}")
        
        lines.extend(["", "ACTION ITEMS:"])
        for item in summary.get('action_items', []):
            if isinstance(item, dict):
                lines.append(f"• {item.get('task', item)}")
            else:
                lines.append(f"• {item}")
        
        lines.extend(["", "NEXT STEPS:"])
        for step in summary.get('next_steps', []):
            lines.append(f"• {step}")
        
        return "\n".join(lines)
    
    def _format_daily_summary(self, summary: Dict[str, Any]) -> str:
        """Format daily summary as plain text"""
        lines = [
            f"DAILY MEETING SUMMARY - {datetime.now().strftime('%B %d, %Y')}",
            f"Total Meetings: {summary.get('total_meetings', 0)}",
            f"Total Duration: {summary.get('total_duration', 0)} minutes",
            "",
            "OVERVIEW:",
            summary.get('daily_summary', 'No meetings today'),
            "",
            "KEY THEMES:",
        ]
        
        for theme in summary.get('key_themes', []):
            lines.append(f"• {theme}")
        
        lines.extend(["", "TODAY'S MEETINGS:"])
        for meeting in summary.get('meeting_titles', []):
            lines.append(f"• {meeting}")
        
        lines.extend(["", "ALL ACTION ITEMS:"])
        for item in summary.get('all_action_items', []):
            if isinstance(item, dict):
                lines.append(f"• {item.get('task', item)}")
            else:
                lines.append(f"• {item}")
        
        return "\n".join(lines)