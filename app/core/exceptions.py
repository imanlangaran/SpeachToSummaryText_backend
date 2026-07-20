"""Domain exceptions — no HTTP knowledge in this file."""


class AppException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(AppException):
    def __init__(self, entity: str, entity_id: int | str | None = None):
        msg = f"{entity} not found" + (f": {entity_id}" if entity_id else "")
        super().__init__(message=msg, code="NOT_FOUND", status_code=404)


class DuplicateError(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, code="DUPLICATE", status_code=409)


class AuthError(AppException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, code="AUTH_ERROR", status_code=401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Admin access required"):
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


class ValidationError(AppException):
    def __init__(self, message: str):
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=400)


class ServiceError(AppException):
    def __init__(self, message: str, code: str = "SERVICE_ERROR"):
        super().__init__(message=message, code=code, status_code=502)
