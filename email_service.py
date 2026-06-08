"""
Email service for sending emails via SMTP
"""

import logging

logger = logging.getLogger(__name__)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
from config import settings

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL or self.smtp_user
        self.app_name = settings.APP_NAME_EMAIL
        self.frontend_url = settings.FRONTEND_URL
        self.email_enabled = settings.EMAIL_ENABLED
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SMTP"""
        if not self.email_enabled:
            logger.debug("Email disabled. Would send to %s", to_email)
            logger.debug("Subject: %s", subject)
            return True
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.app_name} <{self.from_email}>"
            msg['To'] = to_email
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.debug("Email sent to %s", to_email)
            return True
        except Exception as e:
            logger.error("Failed to send email: %s", e)
            return False
    
    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> bool:
        """Send password reset email"""
        reset_link = f"{self.frontend_url}/login?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #4831af 0%, #3a2590 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #4831af; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.app_name}</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>We received a request to reset your password. Click the button below to create a new password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #4831af;">{reset_link}</p>
                    <p><strong>This link will expire in 1 hour.</strong></p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {self.app_name}. All rights reserved.</p>
                    <p>www.jobmouka.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, f"Reset Your {self.app_name} Password", html_content)

    def send_verification_email(self, to_email: str, verification_token: str, user_name: str) -> bool:
        """Send account verification email for HR users"""
        verify_link = f"{self.frontend_url}/login?verify={verification_token}"
        code = verification_token[:6].upper()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #4831af 0%, #3a2590 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 14px 36px; background: #4831af; color: white; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: 600; font-size: 16px; }}
                .code {{ font-size: 32px; font-weight: bold; letter-spacing: 4px; color: #4831af; background: #f0eef5; padding: 16px 32px; border-radius: 8px; display: inline-block; margin: 16px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{self.app_name}</h1>
                    <p>Verify Your HR Account</p>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    <p>Thank you for registering as an HR / Recruiter on <strong>{self.app_name}</strong>.</p>
                    <p>To activate your account and start posting jobs, please verify your email:</p>
                    <p style="text-align: center;">
                        <a href="{verify_link}" class="button">Verify My Account</a>
                    </p>
                    <p>Or use this verification code:</p>
                    <p style="text-align: center;">
                        <span class="code">{code}</span>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #4831af;">{verify_link}</p>
                    <p><strong>This link expires in 24 hours.</strong></p>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
                    <p style="font-size: 13px; color: #6b7280;">Once verified, you'll be able to:</p>
                    <ul style="font-size: 13px; color: #6b7280;">
                        <li>Post job openings</li>
                        <li>View and manage applications</li>
                        <li>Access candidate profiles</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>&copy; 2024 {self.app_name}. All rights reserved.</p>
                    <p>www.jobmouka.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, f"Verify Your {self.app_name} HR Account", html_content)


email_service = EmailService()
