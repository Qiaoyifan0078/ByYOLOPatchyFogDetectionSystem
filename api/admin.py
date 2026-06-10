"""Admin user management routes."""
from flask import Blueprint, g, request

from app import (
    db_conn, ensure_warning_table, execute, json_response,
    query_all, query_one, require_admin,
)

admin_bp = Blueprint('admin', __name__, url_prefix='/api')


@admin_bp.route('/users', methods=['GET'])
@require_admin
def users():
    rows = query_all(
        'SELECT id, username, full_name, role, status, created_at, last_login FROM users ORDER BY id ASC'
    )
    for row in rows:
        row['created_at'] = str(row['created_at'])
        row['last_login'] = str(row['last_login'] or '')
    return json_response({"items": rows})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_admin
def update_user(user_id):
    payload = request.get_json(silent=True) or {}
    role = payload.get("role")
    status = payload.get("status")
    full_name = payload.get("full_name", "")
    phone = payload.get("phone", "")
    if role not in {"admin", "user"} or status not in {"active", "disabled"}:
        return json_response(message='Invalid parameters', status=400)
    execute(
        'UPDATE users SET full_name=%s, phone=%s, role=%s, status=%s WHERE id=%s',
        (full_name, phone, role, status, user_id),
    )
    return json_response()


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    if user_id == g.user["id"]:
        return json_response(message='Cannot delete your own account', status=400)
    ensure_warning_table()
    conn = db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM warning_alerts WHERE user_id=%s', (user_id,))
        cursor.execute('DELETE FROM detections WHERE user_id=%s', (user_id,))
        cursor.execute('DELETE FROM users WHERE id=%s', (user_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return json_response()
