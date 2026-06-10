"""System routes: training stats, health check, metrics."""
import logging
import time

from flask import Blueprint, jsonify, Response, send_from_directory

from app import (
    TRAINING_CHARTS, TRAIN_RUN_DIR,
    get_device, init_db_pool, json_response, require_auth,
)

system_bp = Blueprint('system', __name__, url_prefix='/api')

_start_time = time.time()


@system_bp.route('/training/stats', methods=['GET'])
@require_auth
def training_stats():
    charts = []
    for filename, title in TRAINING_CHARTS:
        path = TRAIN_RUN_DIR / filename
        if path.exists():
            charts.append({
                "filename": filename,
                "title": title,
                "url": "/training-assets/{}?v={}".format(filename, int(path.stat().st_mtime)),
                "size": path.stat().st_size,
            })
    return json_response({"items": charts})


@system_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and load balancers.

    Checks database connectivity and model status.
    """
    status = {'status': 'healthy', 'checks': {}}
    overall = True

    # DB check
    try:
        conn = init_db_pool().get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        status["checks"]["database"] = "ok"
    except Exception as e:
        status["checks"]["database"] = f"error: {str(e)}"
        overall = False

    # Model check
    try:
        from app import _model
        model_loaded = _model is not None
        status["checks"]["model"] = "loaded" if model_loaded else "not_loaded"
    except Exception as e:
        status["checks"]["model"] = f"error: {str(e)}"
        overall = False

    status["checks"]["device"] = get_device()
    status["checks"]["uptime_seconds"] = round(time.time() - _start_time, 1)

    if not overall:
        status["status"] = "degraded"

    return jsonify(status), 200 if overall else 503


@system_bp.route('/metrics', methods=['GET'])
def metrics():
    """Basic Prometheus-compatible metrics endpoint."""
    from app import _model
    metrics_lines = [
        "# HELP fog_detection_uptime_seconds System uptime in seconds",
        "# TYPE fog_detection_uptime_seconds gauge",
        "fog_detection_uptime_seconds {}".format(round(time.time() - _start_time, 1)),
        "# HELP fog_detection_model_loaded Whether the YOLO model is loaded",
        "# TYPE fog_detection_model_loaded gauge",
        "fog_detection_model_loaded {}".format(1 if _model is not None else 0),
        "# HELP fog_detection_device_info GPU/CPU device in use",
        "# TYPE fog_detection_device_info gauge",
        "fog_detection_device_info{{device=\"{}\"}} 1".format(get_device()),
    ]
    return Response("\n".join(metrics_lines), mimetype="text/plain")
