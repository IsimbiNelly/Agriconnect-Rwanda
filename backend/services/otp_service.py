"""In-memory OTP store for password-reset flow.

Each entry: { email -> {"otp": str, "expires": datetime, "attempts": int} }
OTPs expire after OTP_TTL_SECONDS (10 min). Max OTP_MAX_ATTEMPTS before invalidation.
"""
import random
import string
from datetime import datetime, timedelta, timezone

OTP_TTL_SECONDS  = 600   # 10 minutes
OTP_MAX_ATTEMPTS = 5

_store: dict[str, dict] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def generate_otp(email: str) -> str:
    """Generate and store a new 6-digit OTP for the given email. Returns the OTP."""
    otp = "".join(random.choices(string.digits, k=6))
    _store[email.lower()] = {
        "otp":      otp,
        "expires":  _now() + timedelta(seconds=OTP_TTL_SECONDS),
        "attempts": 0,
    }
    return otp


def verify_otp(email: str, otp: str) -> tuple[bool, str]:
    """
    Verify OTP for an email.
    Returns (True, "") on success, or (False, reason) on failure.
    A successful verification removes the OTP from the store.
    """
    key   = email.lower()
    entry = _store.get(key)

    if not entry:
        return False, "No OTP was requested for this email. Please request a new one."

    if _now() > entry["expires"]:
        _store.pop(key, None)
        return False, "OTP has expired. Please request a new code."

    entry["attempts"] += 1
    if entry["attempts"] > OTP_MAX_ATTEMPTS:
        _store.pop(key, None)
        return False, "Too many incorrect attempts. Please request a new code."

    if entry["otp"] != otp.strip():
        remaining = OTP_MAX_ATTEMPTS - entry["attempts"]
        return False, f"Incorrect OTP. {remaining} attempt(s) remaining."

    # Valid — consume the OTP
    _store.pop(key, None)
    return True, ""
