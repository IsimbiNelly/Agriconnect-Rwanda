"""Email service — sends transactional emails via SMTP (TLS)."""
import smtplib
import ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.config.settings import settings

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASS)


def send_email(to: str, subject: str, html: str) -> None:
    """Send an HTML email. Silently logs a warning if SMTP is not configured."""
    if not _smtp_configured():
        logger.warning("[Email] SMTP not configured — skipping email to %s: %s", to, subject)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to
    msg.attach(MIMEText(html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_FROM, to, msg.as_string())
        logger.info("[Email] Sent to %s — %s", to, subject)
    except Exception as exc:
        logger.error("[Email] Failed to send to %s: %s", to, exc)


# ── Email templates ───────────────────────────────────────────────────────────

def send_welcome_email(to: str, full_name: str, username: str, password: str, role: str) -> None:
    role_icon = {"farmer": "🧑‍🌾", "buyer": "🛒", "admin": "🛡️"}.get(role, "👤")
    subject   = "Welcome to AgriConnect! Your account is ready 🌱"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#2d6a4f,#52b788);padding:32px;text-align:center;color:#fff;">
        <div style="font-size:48px;margin-bottom:8px;">🌱</div>
        <h1 style="margin:0;font-size:24px;">Welcome to AgriConnect!</h1>
      </div>
      <div style="padding:28px;">
        <p style="font-size:16px;">Hi <strong>{full_name}</strong>,</p>
        <p>Your account has been created successfully. Here are your details:</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;">
          <tr><td style="padding:8px;color:#6b7280;">Role</td>
              <td style="padding:8px;font-weight:600;">{role_icon} {role.capitalize()}</td></tr>
          <tr style="background:#f9fafb;"><td style="padding:8px;color:#6b7280;">Username</td>
              <td style="padding:8px;font-weight:600;">{username}</td></tr>
          <tr><td style="padding:8px;color:#6b7280;">Email</td>
              <td style="padding:8px;font-weight:600;">{to}</td></tr>
          <tr style="background:#f9fafb;"><td style="padding:8px;color:#6b7280;">Password</td>
              <td style="padding:8px;font-weight:600;font-family:monospace;">{password}</td></tr>
        </table>
        <p style="font-size:13px;color:#6b7280;">Keep your password safe. You can change it anytime from your dashboard.</p>
        <p style="margin-top:24px;">Happy trading,<br><strong>The AgriConnect Team 🌾</strong></p>
      </div>
    </div>
    """
    send_email(to, subject, html)


def send_password_changed_email(to: str, full_name: str, new_password: str) -> None:
    subject = "AgriConnect — Your password has been updated 🔐"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#1e3a5f,#2d6a4f);padding:32px;text-align:center;color:#fff;">
        <div style="font-size:48px;margin-bottom:8px;">🔐</div>
        <h1 style="margin:0;font-size:22px;">Password Updated</h1>
      </div>
      <div style="padding:28px;">
        <p style="font-size:16px;">Hi <strong>{full_name}</strong>,</p>
        <p>Your AgriConnect password has been changed successfully.</p>
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px;margin:16px 0;">
          <p style="margin:0;font-size:13px;color:#166534;">New password:</p>
          <p style="margin:6px 0 0;font-size:18px;font-weight:700;font-family:monospace;color:#166534;">{new_password}</p>
        </div>
        <p style="font-size:13px;color:#6b7280;">If you did not make this change, please contact us immediately.</p>
        <p style="margin-top:24px;">Stay secure,<br><strong>The AgriConnect Team 🌾</strong></p>
      </div>
    </div>
    """
    send_email(to, subject, html)
