"""
Centralized HTTP exception helpers.

All application errors go through these helpers so that error responses
always match the standard APIResponse envelope shape.
"""
from typing import Any, Optional

from fastapi import HTTPException, status


# ── Typed exception subclass ──────────────────────────────────────────────────

class AppException(HTTPException):
    """
    Base application exception that auto-fills `detail` as an envelope dict.
    Raise this (or its subclasses) from services; FastAPI converts it to JSON.
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        data: Optional[Any] = None,
    ) -> None:
        detail = {"success": False, "message": message, "data": data}
        super().__init__(status_code=status_code, detail=detail)


# ── Common 4xx helpers ────────────────────────────────────────────────────────

def not_found(resource: str = "Resource") -> AppException:
    return AppException(
        status_code=status.HTTP_404_NOT_FOUND,
        message=f"{resource} not found.",
    )


def bad_request(message: str) -> AppException:
    return AppException(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=message,
    )


def conflict(message: str) -> AppException:
    return AppException(
        status_code=status.HTTP_409_CONFLICT,
        message=message,
    )


def unauthorized(message: str = "Authentication required.") -> AppException:
    return AppException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message=message,
    )


def forbidden(message: str = "You do not have permission to perform this action.") -> AppException:
    return AppException(
        status_code=status.HTTP_403_FORBIDDEN,
        message=message,
    )


def unprocessable(message: str) -> AppException:
    return AppException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message=message,
    )


def internal_error(message: str = "An unexpected error occurred.") -> AppException:
    return AppException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=message,
    )
