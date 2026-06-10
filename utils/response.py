"""Standardized API response helpers."""
from typing import Any, Dict, List, Optional
from flask import jsonify


def success(
    data: Any = None,
    message: str = "ok",
    status_code: int = 200,
    meta: Optional[Dict] = None,
):
    """Build a standardized success response.

    Args:
        data: Response payload.
        message: Human-readable status message.
        status_code: HTTP status code.
        meta: Optional metadata (pagination info, etc.).

    Returns:
        Flask JSON response tuple.
    """
    body = {'success': True, 'message': message}
    if data is not None:
        body["data"] = data
    if meta:
        body["meta"] = meta
    return jsonify(body), status_code


def paginated(
    items: List,
    total: int,
    page: int = 1,
    page_size: int = 20,
):
    """Build a paginated success response.

    Args:
        items: List of items for the current page.
        total: Total number of items across all pages.
        page: Current page number (1-based).
        page_size: Items per page.

    Returns:
        Flask JSON response tuple.
    """
    return success(
        data={'items': items},
        meta={
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        },
    )


def error(
    message: str = "Error",
    status_code: int = 400,
    error_code: str = "ERROR",
):
    """Build a standardized error response.

    Args:
        message: Human-readable error message.
        status_code: HTTP status code.
        error_code: Machine-readable error identifier.

    Returns:
        Flask JSON response tuple.
    """
    return jsonify({
        'success': False,
        "error_code": error_code,
        "message": message,
    }), status_code
