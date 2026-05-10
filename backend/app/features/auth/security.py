"""
Password hashing (argon2) and JWT creation/verification.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()
_ph = PasswordHasher()


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError):
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────

def _encode(payload: dict[str, Any]) -> str:
    return jwt.encode(payload, settings.APP_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Raise JWTError on invalid/expired tokens."""
    return jwt.decode(token, settings.APP_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def create_access_token(
    user_id: int, org_id: int, role_ids: list[int], is_superuser: bool
) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return _encode(
        {
            "sub": str(user_id),
            "org": org_id,
            "roles": role_ids,
            "is_superuser": is_superuser,
            "type": "access",
            "exp": expire,
        }
    )


def create_refresh_token(user_id: int, org_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    return _encode(
        {
            "sub": str(user_id),
            "org": org_id,
            "type": "refresh",
            "exp": expire,
        }
    )
