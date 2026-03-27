"""Email service — sends transactional emails via SMTP (TLS)."""
import re
import smtplib
import ssl
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.config.settings import settings

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASS)


def _bare_email(addr: str) -> str:
    """Extract bare address from 'Display Name <email@host>' format."""
    m = re.search(r'<(.+?)>', addr)
    return m.group(1).strip() if m else addr.strip()


def send_email(to: str, subject: str, html: str) -> None:
    """Send an HTML email. Logs a warning and returns if SMTP is not configured."""
    if not _smtp_configured():
        logger.warning("[Email] SMTP not configured — skipping email to %s: %s", to, subject)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.SMTP_FROM
    msg["To"]      = to
    msg.attach(MIMEText(html, "html"))

    # sendmail() envelope address must be a bare email (no display name)
    from_addr = _bare_email(settings.SMTP_FROM)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()                            # re-identify after TLS upgrade
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(from_addr, to, msg.as_string())
        logger.info("[Email] Sent '%s' to %s", subject, to)
    except Exception as exc:
        logger.error("[Email] Failed to send '%s' to %s: %s", subject, to, exc)
        raise RuntimeError(f"Email delivery failed: {exc}") from exc


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
    </div>"""
    try:
        send_email(to, subject, html)
    except Exception:
        pass   # welcome email failure must never abort registration


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
    </div>"""
    try:
        send_email(to, subject, html)
    except Exception:
        pass   # password-change email failure must never abort the password update


def send_otp_email(to: str, full_name: str, otp: str) -> None:
    subject = "AgriConnect — Your password reset code 🔑"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
      <div style="background:linear-gradient(135deg,#1e3a5f,#3b82f6);padding:32px;text-align:center;color:#fff;">
        <div style="font-size:48px;margin-bottom:8px;">🔑</div>
        <h1 style="margin:0;font-size:22px;">Password Reset</h1>
      </div>
      <div style="padding:28px;">
        <p style="font-size:16px;">Hi <strong>{full_name}</strong>,</p>
        <p>We received a request to reset your AgriConnect password. Use the code below to verify your identity:</p>
        <div style="background:#eff6ff;border:2px solid #3b82f6;border-radius:12px;padding:24px;margin:20px 0;text-align:center;">
          <p style="margin:0;font-size:13px;color:#1d4ed8;font-weight:600;letter-spacing:1px;">YOUR OTP CODE</p>
          <p style="margin:10px 0 0;font-size:42px;font-weight:800;font-family:monospace;color:#1d4ed8;letter-spacing:10px;">{otp}</p>
        </div>
        <p style="font-size:14px;color:#6b7280;">
          This code expires in <strong>10 minutes</strong>.<br>
          If you did not request a password reset, ignore this email — your account is safe.
        </p>
        <p style="margin-top:24px;">Stay secure,<br><strong>The AgriConnect Team 🌾</strong></p>
      </div>
    </div>"""
    send_email(to, subject, html)
