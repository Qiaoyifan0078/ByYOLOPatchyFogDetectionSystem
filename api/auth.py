"""Authentication routes."""
from flask import Blueprint, g, request
from werkzeug.security import check_password_hash, generate_password_hash

from app import (
    create_token, db_conn, execute, json_response, public_user,
    query_one, require_auth,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    payload = request.get_json(silent=True) or {}
    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    full_name = (payload.get('full_name') or '').strip()
    if len(username) < 3 or len(password) < 6:
        return json_response(message='Username or password format invalid', status=400)
    exists = query_one('SELECT id FROM users WHERE username=%s', (username,))
    if exists:
        return json_response(message='Username already exists', status=409)
    user_id = execute(
        "INSERT INTO users (username, password_hash, full_name, role, status) VALUES (%s, %s, %s, 'user', 'active')",
        (username, generate_password_hash(password), full_name),
    )
    user = query_one('SELECT * FROM users WHERE id=%s', (user_id,))
    return json_response({'token': create_token(user), 'user': public_user(user)})


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    user = query_one('SELECT * FROM users WHERE username=%s', (username,))
    if not user or not check_password_hash(user['password_hash'], password):
        return json_response(message='Invalid username or password', status=401)
    if user['status'] != 'active':
        return json_response(message='Account disabled', status=403)
    execute('UPDATE users SET last_login=NOW() WHERE id=%s', (user['id'],))
    user = query_one('SELECT * FROM users WHERE id=%s', (user['id'],))
    return json_response({'token': create_token(user), 'user': public_user(user)})


@auth_bp.route('/me', methods=['GET'])
@require_auth
def me():
    return json_response({'user': public_user(g.user)})
