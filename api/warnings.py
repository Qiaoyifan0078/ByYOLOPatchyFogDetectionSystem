"""Warning alert routes."""
import logging

from flask import Blueprint, g, request

from app import (
    clean_text, db_conn, ensure_warning_table, execute,
    get_warning_row, json_response, query_all, query_one,
    require_auth, send_warning_sms, serialize_warning,
)

warnings_bp = Blueprint('warnings', __name__, url_prefix='/api')


@warnings_bp.route('/warnings', methods=['GET'])
@require_auth
def warning_alerts():
    ensure_warning_table()
    source_type = request.args.get("source_type", "")
    params = []
    where = []
    if g.user["role"] != "admin":
        where.append('w.user_id=%s')
        params.append(g.user["id"])
    if source_type in {"image", "video", "camera"}:
        where.append('w.source_type=%s')
        params.append(source_type)
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    rows = query_all(
        """SELECT w.id, w.user_id, w.detection_id, w.source_type, w.road_section, w.fog_level,
               w.visibility_level, w.speed_limit, w.snapshot_url, w.status, w.created_at,
               u.username, u.full_name, d.detect_count, d.confidence_max
        FROM warning_alerts w
        JOIN users u ON u.id = w.user_id
        LEFT JOIN detections d ON d.id = w.detection_id
        {}
        ORDER BY w.created_at DESC
        LIMIT 300"""
        .format(where_sql),
        tuple(params),
    )
    return json_response({"items": [serialize_warning(row) for row in rows]})


@warnings_bp.route('/warnings', methods=['POST'])
@require_auth
def create_warning_alert():
    ensure_warning_table()
    payload = request.get_json(silent=True) or {}
    raw_detection_id = payload.get("detection_id")
    detection_id = None
    detection = None
    if raw_detection_id not in (None, ""):
        try:
            detection_id = int(raw_detection_id)
        except (TypeError, ValueError):
            return json_response(message='Invalid detection_id parameter', status=400)
        detection = query_one(
            'SELECT id, user_id, source_type, output_url FROM detections WHERE id=%s',
            (detection_id,),
        )
        if not detection:
            return json_response(message='Detection record not found', status=404)
        if g.user["role"] != "admin" and detection["user_id"] != g.user["id"]:
            return json_response(message='Permission denied', status=403)

    source_type = detection["source_type"] if detection else payload.get("source_type")
    if source_type not in {"image", "video", "camera"}:
        return json_response(message='Invalid alert source type', status=400)

    road_section = clean_text(payload.get("road_section"), 200)
    fog_level = clean_text(payload.get("fog_level"), 60)
    visibility_level = clean_text(payload.get("visibility_level"), 60)
    speed_limit = clean_text(payload.get("speed_limit"), 60)
    if not all([road_section, fog_level, visibility_level, speed_limit]):
        return json_response(message='Please fill in all warning fields', status=400)

    snapshot_url = clean_text(
        payload.get("snapshot_url") or (detection.get("output_url") if detection else ""),
        500,
    )

    alert_id = execute(
        """INSERT INTO warning_alerts
        (user_id, detection_id, source_type, road_section, fog_level, visibility_level, speed_limit, snapshot_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            g.user["id"], detection_id, source_type,
            road_section, fog_level, visibility_level, speed_limit, snapshot_url,
        ),
    )

    try:
        send_warning_sms(
            alert_id, g.user['id'], road_section,
            fog_level, visibility_level, speed_limit
        )
    except Exception as sms_error:
        logging.getLogger(__name__).error(f'SMS send error: {sms_error}')

    return json_response({"item": get_warning_row(alert_id)})


@warnings_bp.route('/warnings/<int:alert_id>', methods=['DELETE'])
@require_auth
def delete_warning_alert(alert_id):
    ensure_warning_table()
    alert = query_one('SELECT * FROM warning_alerts WHERE id=%s', (alert_id,))
    if not alert:
        return json_response(message='Warning record not found', status=404)
    if g.user["role"] != "admin" and alert["user_id"] != g.user["id"]:
        return json_response(message='Permission denied', status=403)
    execute('DELETE FROM warning_alerts WHERE id=%s', (alert_id,))
    return json_response()
