"""
Custom exception types and FastAPI exception handlers.
Register handlers in main.py via add_exception_handler().
"""
from fastapi import Request
from fastapi.responses import JSONResponse


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------

class AppError(Exception):
    """Base class for all application errors."""
    status_code: int = 500
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class AuthenticationError(AppError):
    """Raised when JWT verification fails or token is missing."""
    status_code = 401
    detail = "Authentication required"


class ForbiddenError(AppError):
    """Raised when an authenticated user tries to access another org's data."""
    status_code = 403
    detail = "Access forbidden"


class NotFoundError(AppError):
    """Raised when a requested resource does not exist (or is not accessible)."""
    status_code = 404
    detail = "Resource not found"


class ConflictError(AppError):
    """Raised on duplicate resource creation."""
    status_code = 409
    detail = "Resource already exists"


class UnprocessableError(AppError):
    """Raised for business-logic validation failures beyond Pydantic."""
    status_code = 422
    detail = "Unprocessable entity"


# ---------------------------------------------------------------------------
# FastAPI exception handlers
# ---------------------------------------------------------------------------

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
