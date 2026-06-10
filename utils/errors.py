"""Custom exception classes and Flask error handlers."""
import logging
from flask import jsonify, request

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error with HTTP status code."""
    status_code: int = 500
    message: str = 'Internal server error'
    error_code: str = 'INTERNAL_ERROR'

    def __init__(self, message=None, status_code=None, error_code=None, payload=None):
        super().__init__(message or self.message)
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.payload = payload or {}

    def to_dict(self):
        return {
            'success': False,
            'error_code': self.error_code,
            'message': self.message,
            **self.payload,
        }


class BadRequestError(AppError):
    status_code = 400
    error_code = 'BAD_REQUEST'
    message = 'Bad request'


class UnauthorizedError(AppError):
    status_code = 401
    error_code = 'UNAUTHORIZED'
    message = "Authentication required"


class ForbiddenError(AppError):
    status_code = 403
    error_code = 'FORBIDDEN'
    message = "Permission denied"


class NotFoundError(AppError):
    status_code = 404
    error_code = 'NOT_FOUND'
    message = "Resource not found"


class ConflictError(AppError):
    status_code = 409
    error_code = 'CONFLICT'
    message = "Resource conflict"


class ValidationError(AppError):
    status_code = 422
    error_code = 'VALIDATION_ERROR'
    message = "Validation failed"

    def __init__(self, message=None, errors=None):
        super().__init__(message=message or self.message)
        self.errors = errors or {}

    def to_dict(self):
        d = super().to_dict()
        if self.errors:
            d["errors"] = self.errors
        return d


class RateLimitError(AppError):
    status_code = 429
    error_code = 'RATE_LIMITED'
    message = "Too many requests"


class ServiceUnavailableError(AppError):
    status_code = 503
    error_code = 'SERVICE_UNAVAILABLE'
    message = "Service temporarily unavailable"


def register_error_handlers(app):
    """Register global error handlers on the Flask app."""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        logger.warning(
            "AppError: %s [%s] %s",
            error.error_code,
            error.status_code,
            error.message,
            extra={"path": request.path, "method": request.method},
        )
        return jsonify(error.to_dict()), error.status_code

    @app.errorhandler(400)
    def handle_400(error):
        return jsonify(BadRequestError(str(error)).to_dict()), 400

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify(NotFoundError(str(error)).to_dict()), 404

    @app.errorhandler(405)
    def handle_405(error):
        return jsonify({
            'success': False,
            'error_code': 'METHOD_NOT_ALLOWED',
            "message": "Method not allowed",
        }), 405

    @app.errorhandler(500)
    def handle_500(error):
        original = getattr(error, 'original_exception', error)
        logger.exception(
            "Unhandled exception: %s",
            str(original),
            extra={"path": request.path, "method": request.method},
        )
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            "message": "An unexpected error occurred",
        }), 500

    @app.errorhandler(413)
    def handle_413(error):
        return jsonify({
            'success': False,
            'error_code': 'PAYLOAD_TOO_LARGE',
            "message": "Upload file too large",
        }), 413
