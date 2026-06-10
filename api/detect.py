"""Image and video detection routes."""
import json
import time
import uuid

import cv2
import numpy as np
from flask import Blueprint, g, request, send_from_directory

from app import (
    IMAGE_EXTS, OUTPUT_DIR, UPLOAD_DIR, VIDEO_EXTS,
    create_browser_video_writer, db_conn, detect_frame, draw_boxes,
    execute, get_model, insert_detection, json_response,
    query_all, query_one, read_image, require_auth,
    save_upload, summarize, write_image,
)

detect_bp = Blueprint('detect', __name__, url_prefix='/api')


@detect_bp.route('/detect/image', methods=['POST'])
@require_auth
def detect_image():
    if "file" not in request.files:
        return json_response(message='File is required', status=400)
    file_storage = request.files["file"]
    source_type = request.form.get("source_type", "image")
    if source_type not in {"image", "camera"}:
        source_type = "image"
    conf = float(request.form.get("conf", 0.25))
    original_name, input_path = save_upload(file_storage, source_type)
    if input_path.suffix.lower() not in IMAGE_EXTS:
        return json_response(message='File format not supported', status=400)
    start = time.time()
    image = read_image(input_path)
    if image is None:
        return json_response(message='Image read failed', status=400)
    detections = detect_frame(image, conf=conf)
    rendered = draw_boxes(image, detections)
    output_name = "{}.jpg".format(uuid.uuid4().hex)
    output_path = OUTPUT_DIR / output_name
    write_image(output_path, rendered)
    duration_ms = int((time.time() - start) * 1000)
    detection_id, count, avg_conf, max_conf = insert_detection(
        g.user["id"], source_type, original_name,
        input_path, output_path,
        "/outputs/{}".format(output_name),
        detections, duration_ms,
        {"width": int(image.shape[1]), "height": int(image.shape[0]), "conf": conf},
    )
    return json_response({
        "id": detection_id,
        "output_url": "/outputs/{}".format(output_name),
        "detections": detections,
        "count": count,
        "confidence_avg": round(avg_conf, 4),
        "confidence_max": round(max_conf, 4),
        "duration_ms": duration_ms,
    })


@detect_bp.route('/detect/video', methods=['POST'])
@require_auth
def detect_video():
    if "file" not in request.files:
        return json_response(message='File is required', status=400)
    frame_step = max(1, min(30, int(request.form.get("frame_step", 5))))
    conf = float(request.form.get("conf", 0.25))
    original_name, input_path = save_upload(request.files["file"], "video")
    if input_path.suffix.lower() not in VIDEO_EXTS:
        return json_response(message='File format not supported', status=400)
    start = time.time()
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        return json_response(message='Video read failed', status=400)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    output_name, output_path, writer = create_browser_video_writer(
        uuid.uuid4().hex, fps, width, height)
    all_detections = []
    cached_detections = []
    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index % frame_step == 0:
            cached_detections = detect_frame(frame, conf=conf)
            for item in cached_detections:
                copied = dict(item)
                copied["frame_index"] = frame_index
                all_detections.append(copied)
        rendered = draw_boxes(frame, cached_detections)
        writer.write(rendered)
        frame_index += 1
    cap.release()
    writer.release()
    duration_ms = int((time.time() - start) * 1000)
    detection_id, count, avg_conf, max_conf = insert_detection(
        g.user["id"], "video", original_name,
        input_path, output_path,
        "/outputs/{}".format(output_name),
        all_detections, duration_ms,
        {
            "fps": float(fps), "width": width, "height": height,
            "frames": frame_index or total_frames, "frame_step": frame_step,
            "conf": conf,
        },
    )
    return json_response({
        "id": detection_id,
        "output_url": "/outputs/{}".format(output_name),
        "count": count,
        "confidence_avg": round(avg_conf, 4),
        "confidence_max": round(max_conf, 4),
        "duration_ms": duration_ms,
    })


@detect_bp.route('/detections', methods=['GET'])
@require_auth
def detections():
    source_type = request.args.get("source_type", "")
    params = []
    where = []
    if g.user["role"] != "admin":
        where.append('d.user_id=%s')
        params.append(g.user["id"])
    if source_type in {"image", "video", "camera"}:
        where.append('d.source_type=%s')
        params.append(source_type)
    where_sql = "WHERE " + " AND ".join(where) if where else ""
    rows = query_all(
        """SELECT d.id, d.source_type, d.original_name, d.output_url, d.detect_count,
               d.confidence_avg, d.confidence_max, d.duration_ms, d.created_at,
               u.username, u.full_name
        FROM detections d
        JOIN users u ON u.id = d.user_id
        {}
        ORDER BY d.created_at DESC
        LIMIT 200"""
        .format(where_sql),
        tuple(params),
    )
    for row in rows:
        row['created_at'] = str(row['created_at'])
        row['confidence_avg'] = float(row['confidence_avg'])
        row['confidence_max'] = float(row['confidence_max'])
    return json_response({"items": rows})


@detect_bp.route('/detections/<int:detection_id>', methods=['DELETE'])
@require_auth
def delete_detection(detection_id):
    detection = query_one('SELECT * FROM detections WHERE id=%s', (detection_id,))
    if not detection:
        return json_response(message='Record not found', status=404)
    if g.user["role"] != "admin" and detection["user_id"] != g.user["id"]:
        return json_response(message='Permission denied', status=403)
    execute('DELETE FROM detections WHERE id=%s', (detection_id,))
    return json_response()
