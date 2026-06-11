import os
import logging
import secrets
import requests

logger = logging.getLogger(__name__)

# Resend API configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
MAIL_FROM = os.environ.get('MAIL_FROM', 'Prayaas <noreply@prayaas.tech>')
BASE_URL = os.environ.get('BASE_URL', 'https://www.prayaas.tech')


def generate_verification_token():
    """Generate a cryptographically secure verification token."""
    return secrets.token_urlsafe(48)


def send_verification_email(to_email, student_name, token):
    """
    Send a verification email via Resend API.
    Falls back to logging the URL if RESEND_API_KEY is not set.
    """
    verify_url = f"{BASE_URL}/verify/{token}"

    if not RESEND_API_KEY:
        logger.info("=========================================")
        logger.info("EMAIL VERIFICATION (dev mode - no API key)")
        logger.info(f"To: {to_email}")
        logger.info(f"Verify URL: {verify_url}")
        logger.info("=========================================")
        return True

    html = f"""
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
            Thanks for registering on Prayaas. Please verify your email address to activate your account and start finding internships.
          </p>
          <div style="text-align:center;margin:0 0 24px;">
            <a href="{verify_url}"
               style="display:inline-block;padding:14px 48px;background:linear-gradient(135deg,#00d4ff,#7b61ff);color:#fff;font-size:16px;font-weight:600;text-decoration:none;border-radius:10px;">
              Verify Email Address
            </a>
          </div>
          <p style="color:#666;font-size:13px;line-height:1.5;margin:0 0 8px;">
            If the button doesn't work, copy and paste this link into your browser:
          </p>
          <p style="color:#00d4ff;font-size:13px;word-break:break-all;margin:0;">
            <a href="{verify_url}" style="color:#00d4ff;">{verify_url}</a>
          </p>
        </div>
        <div style="padding:20px 40px;border-top:1px solid rgba(255,255,255,.06);text-align:center;">
          <p style="color:#444;font-size:12px;margin:0;">
            This link expires in 24 hours. If you didn't create an account, ignore this email.
          </p>
        </div>
      </div>
    </body>
    </html>
    """

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": MAIL_FROM,
                "to": [to_email],
                "subject": "Verify your Prayaas account",
                "html": html,
            },
            timeout=15,
        )

        if resp.status_code == 200:
            logger.info(f"Verification email sent to {to_email}")
            return True
        else:
            logger.error(f"Resend API error {resp.status_code}: {resp.text}")
            logger.info(f"Verify URL (fallback): {verify_url}")
            return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        logger.info(f"Verify URL (fallback): {verify_url}")
        return True
