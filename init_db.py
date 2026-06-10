from __future__ import annotations

import os

import mysql.connector
from werkzeug.security import generate_password_hash


DB_HOST = os.getenv("FOG_DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("FOG_DB_PORT", "3307"))
DB_USER = os.getenv("FOG_DB_USER", "root")
DB_PASSWORD = os.getenv("FOG_DB_PASSWORD", "123456")
DB_NAME = os.getenv("FOG_DB_NAME", "patchy_fog_system")


def connect(database=None):
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=database,
        autocommit=False,
    )


def execute_many(cursor, statements):
    for statement in statements:
        cursor.execute(statement)


def main():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(DB_NAME)
    )
    conn.commit()
    cursor.close()
    conn.close()

    conn = connect(DB_NAME)
    cursor = conn.cursor()
    execute_many(
        cursor,
        [
             """
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(64) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(80) DEFAULT '',
                phone VARCHAR(20) DEFAULT '',
                wechat_openid VARCHAR(128) DEFAULT NULL,
                role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
                status ENUM('active', 'disabled') NOT NULL DEFAULT 'active',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_login DATETIME NULL,
                INDEX idx_wechat_openid (wechat_openid)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS detections (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                source_type ENUM('image', 'video', 'camera') NOT NULL,
                original_name VARCHAR(255) NOT NULL,
                input_path VARCHAR(500) NOT NULL,
                output_path VARCHAR(500) NOT NULL,
                output_url VARCHAR(500) NOT NULL,
                status ENUM('success', 'failed') NOT NULL DEFAULT 'success',
                detect_count INT NOT NULL DEFAULT 0,
                confidence_avg DECIMAL(8, 4) NOT NULL DEFAULT 0,
                confidence_max DECIMAL(8, 4) NOT NULL DEFAULT 0,
                duration_ms INT NOT NULL DEFAULT 0,
                metadata JSON NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_detections_user_time (user_id, created_at),
                INDEX idx_detections_source_time (source_type, created_at),
                CONSTRAINT fk_detections_user FOREIGN KEY (user_id) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS detection_items (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                detection_id BIGINT NOT NULL,
                class_name VARCHAR(64) NOT NULL,
                confidence DECIMAL(8, 4) NOT NULL,
                bbox_x1 INT NOT NULL,
                bbox_y1 INT NOT NULL,
                bbox_x2 INT NOT NULL,
                bbox_y2 INT NOT NULL,
                frame_index INT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_items_detection (detection_id),
                CONSTRAINT fk_items_detection FOREIGN KEY (detection_id) REFERENCES detections(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
             """
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS system_events (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id BIGINT NULL,
                event_type VARCHAR(64) NOT NULL,
                content VARCHAR(500) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_events_time (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
        ],
    )

    admin_hash = generate_password_hash("123456")
    user_hash = generate_password_hash("123456")
    cursor.execute(
        """
        INSERT INTO users (username, password_hash, full_name, role, status)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            role = VALUES(role),
            status = VALUES(status),
            full_name = VALUES(full_name)
        """,
        ("admin", admin_hash, "系统管理员", "admin", "active"),
    )
    cursor.execute(
        """
        INSERT INTO users (username, password_hash, full_name, role, status)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE username = username
        """,
        ("operator", user_hash, "检测员", "user", "active"),
    )
    cursor.execute(
        """
        INSERT INTO system_events (event_type, content)
        VALUES (%s, %s)
        """,
        ("database_init", "database initialized"),
    )
    conn.commit()
    cursor.close()
    conn.close()
    print("database initialized: {}".format(DB_NAME))
    print("admin account: admin / 123456")
    print("operator account: operator / 123456")


if __name__ == "__main__":
    main()
