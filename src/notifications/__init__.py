"""
Notifications package for Meeting Agent
"""

from .sender import EmailSender, MockEmailSender

__all__ = ["EmailSender", "MockEmailSender"]