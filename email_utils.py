import os
import logging
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# Configuration
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.testmail.app')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', 'apikey')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', 'cd3045f4-c1e8-4ec5-aa03-e9c86ad97ff0')
MAIL_FROM = os.environ.get('MAIL_FROM', 'Prayaas <noreply@r7jex.testmail.app>')
BASE_URL = os.environ.get('BASE_URL', 'https://sih-2025-project-2.onrender.com')

# Resend API (backup)
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')


def generate_verification_token():
    """Generate a cryptographically secure verification token."""
    return secrets.token_urlsafe(48)


def _build_email_html(student_name, verify_url):
    """Build the verification email HTML."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#0a0a1a;font-family:'Segoe UI',Arial,sans-serif;">
      <div style="max-width:520px;margin:40px auto;background:#12122a;border-radius:16px;border:1px solid rgba(255,255,255,.08);overflow:hidden;">
        <div style="padding:32px 40px;text-align:center;border-bottom:1px solid rgba(255,255,255,.06);">
          <h1 style="color:#00d4ff;font-size:24px;margin:0;">Prayaas</h1>
        </div>
        <div style="padding:32px 40px;">
          <h2 style="color:#fff;font-size:20px;margin:0 0 16px;">Verify your email</h2>
          <p style="color:#a0a0b8;font-size:15px;line-height:1.6;margin:0 0 24px;">
            Hi {student_name},<br><br>
            Thanks for registering on Prayaas. Please verify your email to activate your account.
          </p>
          <div style="text-align:center;margin:0 0 24px;">
            <a href="{verify_url}"
               style="display:inline-block;padding:14px 48px;background:linear-gradient(135deg,#00d4ff,#7b61ff);color:#fff;font-size:16px;font-weight:600;text-decoration:none;border-radius:10px;">
              Verify Email Address
            </a>
          </div>
          <p style="color:#666;font-size:13px;line-height:1.5;margin:0 0 8px;">
            Or copy this link into your browser:
          </p>
          <p style="color:#00d4ff;font-size:13px;word-break:break-all;margin:0;">
            <a href="{verify_url}" style="color:#00d4ff;">{verify_url}</a>
          </p>
        </div>
        <div style="padding:20px 40px;border-top:1px solid rgba(255,255,255,.06);text-align:center;">
          <p style="color:#444;font-size:12px;margin:0;">This link expires in 24 hours.</p>
        </div>
      </div>
    </body>
    </html>
    """


def _send_via_smtp(to_email, subject, html):
    """Send email via SMTP."""
    text = f"Verify your email: {BASE_URL}/verify/token"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = MAIL_FROM
    msg['To'] = to_email
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(MAIL_FROM, to_email, msg.as_string())


def _send_via_resend(to_email, subject, html):
    """Send email via Resend API."""
    import requests as req
    resp = req.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Prayaas <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": html,
        },
        timeout=15,
    )
    if resp.status_code != 200:
        raise Exception(f"Resend API error {resp.status_code}: {resp.text}")


def send_verification_email(to_email, student_name, token):
    """Send verification email. Tries SMTP first, falls back to Resend API."""
    verify_url = f"{BASE_URL}/verify/{token}"
    subject = "Verify your Prayaas account"
    html = _build_email_html(student_name, verify_url)

    # Try SMTP first
    try:
        logger.info(f"Attempting SMTP send to {to_email} via {SMTP_HOST}:{SMTP_PORT}")
        _send_via_smtp(to_email, subject, html)
        logger.info(f"Email sent via SMTP to {to_email}")
        return True
    except Exception as e:
        logger.error(f"SMTP failed for {to_email}: {type(e).__name__}: {e}")

    # Fallback to Resend API
    if RESEND_API_KEY:
        try:
            _send_via_resend(to_email, subject, html)
            logger.info(f"Email sent via Resend to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Resend failed for {to_email}: {type(e).__name__}: {e}")

    logger.error(f"ALL EMAIL METHODS FAILED for {to_email}. Verify URL: {verify_url}")
    return False
