from __future__ import annotations

import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from threading import Lock

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import cv2
import jwt
import mysql.connector
import torch
from mysql.connector.pooling import MySQLConnectionPool
import numpy as np
from flask import Flask, Response, g, jsonify, request, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from sms_service import sms_service


ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT / "uploads"
OUTPUT_DIR = ROOT / "outputs"
FRONTEND_DIST = ROOT / "frontend" / "dist"
MODEL_PATH = ROOT / "runs" / "detect" / "patchy_fog_yolov8n" / "weights" / "best.pt"
TRAIN_RUN_DIR = ROOT / "runs" / "detect" / "patchy_fog_yolov8n"
FALLBACK_MODEL_PATH = ROOT / "yolov8n.pt"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm"}
TRAINING_CHARTS = [
    ("results.png", "Training Results"),
    ("F1_curve.png", "F1 Curve"),
    ("P_curve.png", "P Curve"),
    ("PR_curve.png", "PR Curve"),
    ("R_curve.png", "R Curve"),
]

DB_HOST = os.getenv("FOG_DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("FOG_DB_PORT", "3307"))
DB_USER = os.getenv("FOG_DB_USER", "root")
DB_PASSWORD = os.getenv("FOG_DB_PASSWORD", "123456")
DB_NAME = os.getenv("FOG_DB_NAME", "patchy_fog_system")
JWT_SECRET = os.getenv("FOG_JWT_SECRET", "patchy-fog-system-secret")

app = Flask(__name__, static_folder=str(FRONTEND_DIST), static_url_path="")
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 600
CORS(app)

import sys
if sys.platform == 'win32':
    os.environ['PYTHONUTF8'] = '1'

__model = None
__model_lock = Lock()
__db_pool = None
def init_db_pool():
    global __db_pool
    if __db_pool is not None:
        return __db_pool
    with __model_lock:
        if __db_pool is None:
            __db_pool = MySQLConnectionPool(
                pool_name="fog_detection_pool",
                pool_size=5,
                pool_reset_session=True,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                autocommit=False,
            )
        return __db_pool



def get_device():
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

DEVICE = get_device()


def ensure_dirs():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def db_conn():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        autocommit=False,
    )


def query_one(sql, params=None):
    conn = db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def query_all(sql, params=None):
    conn = db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def execute(sql, params=None):
    conn = db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def ensure_warning_table():
    conn = db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warning_alerts (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                detection_id BIGINT NULL,
                source_type ENUM('image', 'video', 'camera') NOT NULL,
                road_section VARCHAR(200) NOT NULL,
                fog_level VARCHAR(60) NOT NULL,
                visibility_level VARCHAR(60) NOT NULL,
                speed_limit VARCHAR(60) NOT NULL,
                snapshot_url VARCHAR(500) DEFAULT '',
                status ENUM('active', 'handled') NOT NULL DEFAULT 'active',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_warning_user_time (user_id, created_at),
                INDEX idx_warning_detection (detection_id),
                INDEX idx_warning_source_time (source_type, created_at),
                CONSTRAINT fk_warning_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_warning_detection FOREIGN KEY (detection_id) REFERENCES detections(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
        )
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sms_logs (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                warning_id BIGINT NULL,
                phone VARCHAR(20) NOT NULL,
                content VARCHAR(500) NOT NULL,
                status ENUM('pending', 'success', 'failed') NOT NULL DEFAULT 'pending',
                error_message VARCHAR(500) DEFAULT NULL,
                sent_at DATETIME NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_sms_warning (warning_id),
                INDEX idx_sms_phone_time (phone, created_at),
                CONSTRAINT fk_sms_warning FOREIGN KEY (warning_id) REFERENCES warning_alerts(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"""
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def clean_text(value, max_length):
    return str(value or "").strip()[:max_length]


def serialize_warning(row):
    row["created_at"] = str(row["created_at"])
    row["confidence_max"] = float(row["confidence_max"] or 0)
    row["detect_count"] = int(row["detect_count"] or 0)
    return row


def get_warning_row(alert_id):
    row = query_one("""
        SELECT w.id, w.user_id, w.detection_id, w.source_type, w.road_section, w.fog_level,
               w.visibility_level, w.speed_limit, w.snapshot_url, w.status, w.created_at,
               u.username, u.full_name, d.detect_count, d.confidence_max
        FROM warning_alerts w
        JOIN users u ON u.id = w.user_id
        LEFT JOIN detections d ON d.id = w.detection_id
        WHERE w.id=%s
        """, (alert_id,))
    return serialize_warning(row) if row else None


def create_token(user):
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=12),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def public_user(user):
    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user.get("full_name") or "",
        "role": user["role"],
        "status": user["status"],
        "created_at": str(user.get("created_at") or ""),
        "last_login": str(user.get("last_login") or ""),
    }


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"message": "Unauthorized"}), 401
        token = header.replace("Bearer ", "", 1).strip()
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            return jsonify({"message": "Unauthorized"}), 401
        user = query_one("SELECT * FROM users WHERE id=%s", (payload.get("sub"),))
        if not user or user["status"] != "active":
            return jsonify({"message": "Forbidden"}), 403
        g.user = user
        return fn(*args, **kwargs)
    return wrapper


def require_admin(fn):
    @wraps(fn)
    @require_auth
    def wrapper(*args, **kwargs):
        if g.user["role"] != "admin":
            return jsonify({"message": "Forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper


def get_model():
    global __model
    with __model_lock:
        if __model is None:
            model_path = MODEL_PATH if MODEL_PATH.exists() else FALLBACK_MODEL_PATH
            __model = YOLO(str(model_path))
        return __model


def json_response(data=None, message="success", status=200):
    body = {"message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status


def save_upload(file_storage, folder):
    original_name = secure_filename(file_storage.filename or "upload")
    ext = Path(original_name).suffix.lower()
    unique_name = "{}{}".format(uuid.uuid4().hex, ext)
    target_dir = UPLOAD_DIR / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / unique_name
    file_storage.save(str(target))
    return original_name, target


def read_image(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def write_image(path, image):
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".jpg", image)
    if not ok:
        raise RuntimeError("image encode failed")
    encoded.tofile(str(path))


def create_browser_video_writer(base_name, fps, width, height):
    output_name = "{}.webm".format(base_name)
    output_path = OUTPUT_DIR / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"VP80"), fps, (width, height))
    if not writer.isOpened():
        output_name = "{}.mp4".format(base_name)
        output_path = OUTPUT_DIR / output_name
        writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"avc1"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError("video encoder unavailable")
    return output_name, output_path, writer


def draw_boxes(image, detections):
    canvas = image.copy()
    for item in detections:
        x1, y1, x2, y2 = item["bbox"]
        conf = item["confidence"]
        color = (28, 132, 255)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        label = "{} {:.2f}".format(item["class_name"], conf)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.62, 2)
        cv2.rectangle(canvas, (x1, max(0, y1 - th - 12)), (x1 + tw + 10, y1), color, -1)
        cv2.putText(canvas, label, (x1 + 5, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2)
    return canvas


def detect_frame(image, conf=0.25):
    model = get_model()
    result = model.predict(source=image, imgsz=640, conf=conf, device=DEVICE, verbose=False)[0]
    detections = []
    names = result.names
    if result.boxes is None:
        return detections
    boxes = result.boxes.xyxy.cpu().numpy()
    scores = result.boxes.conf.cpu().numpy()
    classes = result.boxes.cls.cpu().numpy()
    height, width = image.shape[:2]
    for box, score, cls_id in zip(boxes, scores, classes):
        x1, y1, x2, y2 = [int(round(v)) for v in box.tolist()]
        x1 = max(0, min(width - 1, x1))
        x2 = max(0, min(width - 1, x2))
        y1 = max(0, min(height - 1, y1))
        y2 = max(0, min(height - 1, y2))
        detections.append(
            {
                "class_name": names.get(int(cls_id), "patchy_fog"),
                "confidence": float(score),
                "bbox": [x1, y1, x2, y2],
            }
        )
    return detections


def summarize(detections):
    if not detections:
        return 0, 0.0, 0.0
    scores = [item["confidence"] for item in detections]
    return len(detections), float(sum(scores) / len(scores)), float(max(scores))


def insert_detection(user_id, source_type, original_name, input_path, output_path, output_url, detections, duration_ms, metadata):
    count, avg_conf, max_conf = summarize(detections)
    conn = db_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO detections
            (user_id, source_type, original_name, input_path, output_path, output_url, detect_count,
             confidence_avg, confidence_max, duration_ms, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, source_type, original_name, str(input_path), str(output_path), output_url, count, round(avg_conf, 4), round(max_conf, 4), duration_ms, json.dumps(metadata, ensure_ascii=False)),
        )
        detection_id = cursor.lastrowid
        for item in detections[:1000]:
            x1, y1, x2, y2 = item["bbox"]
            cursor.execute(
                """INSERT INTO detection_items
                (detection_id, class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, frame_index)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (detection_id, item["class_name"], round(item["confidence"], 4), x1, y1, x2, y2, item.get("frame_index")),
            )
        conn.commit()
        return detection_id, count, avg_conf, max_conf
    finally:
        cursor.close()
        conn.close()


def send_warning_sms(warning_id, user_id, road_section, fog_level, visibility_level, speed_limit):
    user = query_one("SELECT phone FROM users WHERE id=%s", (user_id,))
    if not user or not user.get("phone"):
        return False
    phone = user["phone"]
    sms_log_id = execute("""INSERT INTO sms_logs (warning_id, phone, content, status) VALUES (%s, %s, %s, 'pending')""", (warning_id, phone, f"{road_section} {fog_level} {visibility_level} {speed_limit}"))
    try:
        result = sms_service.send_sms(phone, road_section, fog_level, visibility_level, speed_limit)
        if result["success"]:
            execute("UPDATE sms_logs SET status='success', sent_at=NOW(), error_message=NULL WHERE id=%s", (sms_log_id,))
            return True
        else:
            execute("UPDATE sms_logs SET status='failed', error_message=%s WHERE id=%s", (result["message"], sms_log_id))
            return False
    except Exception as e:
        execute("UPDATE sms_logs SET status='failed', error_message=%s WHERE id=%s", (str(e), sms_log_id))
        return False

####################### Middleware #######################

@app.before_request
def _assign_request_id():
    g.request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:12])


@app.after_request
def _add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Request-ID"] = getattr(g, "request_id", "-")
    return response

####################### Static Serving Routes ######################

@app.route("/training-assets/<path:filename>")
def training_assets(filename):
    allowed = {name for name, _ in TRAINING_CHARTS}
    if filename not in allowed:
        return Response(status=404)
    return send_from_directory(str(TRAIN_RUN_DIR), filename)


@app.route("/outputs/<path:filename>")
def outputs(filename):
    return send_from_directory(str(OUTPUT_DIR), filename)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def frontend(path):
    if path.startswith("api/"):
        return Response(status=404)
    target = FRONTEND_DIST / path
    if path and target.exists() and target.is_file():
        return send_from_directory(str(FRONTEND_DIST), path)
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return send_from_directory(str(FRONTEND_DIST), "index.html")
    return jsonify({"message": "frontend not built"}), 404


ensure_dirs()

if __name__ == "__main__":
    from api.auth import auth_bp
    from api.detect import detect_bp
    from api.warnings import warnings_bp
    from api.admin import admin_bp
    from api.system import system_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(detect_bp)
    app.register_blueprint(warnings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(system_bp)

    app.run(host="0.0.0.0", port=5001, debug=False)
