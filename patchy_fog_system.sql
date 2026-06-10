/*
 Navicat Premium Dump SQL

 Source Server         : 1
 Source Server Type    : MySQL
 Source Server Version : 50726 (5.7.26)
 Source Host           : localhost:3307
 Source Schema         : patchy_fog_system

 Target Server Type    : MySQL
 Target Server Version : 50726 (5.7.26)
 File Encoding         : 65001

 Date: 01/05/2026 20:40:14
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for detection_items
-- ----------------------------
DROP TABLE IF EXISTS `detection_items`;
CREATE TABLE `detection_items`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `detection_id` bigint(20) NOT NULL,
  `class_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `confidence` decimal(8, 4) NOT NULL,
  `bbox_x1` int(11) NOT NULL,
  `bbox_y1` int(11) NOT NULL,
  `bbox_x2` int(11) NOT NULL,
  `bbox_y2` int(11) NOT NULL,
  `frame_index` int(11) NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_items_detection`(`detection_id`) USING BTREE,
  CONSTRAINT `fk_items_detection` FOREIGN KEY (`detection_id`) REFERENCES `detections` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 54 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of detection_items
-- ----------------------------
INSERT INTO `detection_items` VALUES (2, 2, 'patchy_fog', 0.8487, 0, 41, 509, 286, NULL, '2026-05-01 20:05:12');
INSERT INTO `detection_items` VALUES (3, 3, 'patchy_fog', 0.9589, 45, 92, 1207, 693, 0, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (4, 3, 'patchy_fog', 0.9586, 46, 92, 1208, 693, 5, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (5, 3, 'patchy_fog', 0.9609, 194, 89, 1080, 691, 10, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (6, 3, 'patchy_fog', 0.9708, 0, 94, 1272, 698, 15, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (7, 3, 'patchy_fog', 0.9707, 0, 94, 1272, 698, 20, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (8, 3, 'patchy_fog', 0.9591, 130, 90, 1133, 693, 25, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (9, 3, 'patchy_fog', 0.9001, 77, 90, 1205, 687, 30, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (10, 3, 'patchy_fog', 0.8963, 77, 90, 1205, 687, 35, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (11, 3, 'patchy_fog', 0.9300, 127, 83, 1138, 673, 40, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (12, 3, 'patchy_fog', 0.9437, 1, 92, 1272, 690, 45, '2026-05-01 20:21:39');
INSERT INTO `detection_items` VALUES (18, 5, 'patchy_fog', 0.9589, 45, 92, 1207, 693, 0, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (19, 5, 'patchy_fog', 0.9586, 46, 92, 1208, 693, 5, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (20, 5, 'patchy_fog', 0.9609, 194, 89, 1080, 691, 10, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (21, 5, 'patchy_fog', 0.9708, 0, 94, 1272, 698, 15, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (22, 5, 'patchy_fog', 0.9707, 0, 94, 1272, 698, 20, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (23, 5, 'patchy_fog', 0.9591, 130, 90, 1133, 693, 25, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (24, 5, 'patchy_fog', 0.9001, 77, 90, 1205, 687, 30, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (25, 5, 'patchy_fog', 0.8963, 77, 90, 1205, 687, 35, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (26, 5, 'patchy_fog', 0.9300, 127, 83, 1138, 673, 40, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (27, 5, 'patchy_fog', 0.9437, 1, 92, 1272, 690, 45, '2026-05-01 20:27:59');
INSERT INTO `detection_items` VALUES (28, 6, 'patchy_fog', 0.9694, 0, 45, 1279, 954, NULL, '2026-05-01 20:31:21');
INSERT INTO `detection_items` VALUES (29, 7, 'patchy_fog', 0.9693, 0, 96, 1269, 698, NULL, '2026-05-01 20:31:51');
INSERT INTO `detection_items` VALUES (31, 9, 'patchy_fog', 0.9589, 45, 92, 1207, 693, 0, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (32, 9, 'patchy_fog', 0.9586, 46, 92, 1208, 693, 5, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (33, 9, 'patchy_fog', 0.9609, 194, 89, 1080, 691, 10, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (34, 9, 'patchy_fog', 0.9708, 0, 94, 1272, 698, 15, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (35, 9, 'patchy_fog', 0.9707, 0, 94, 1272, 698, 20, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (36, 9, 'patchy_fog', 0.9591, 130, 90, 1133, 693, 25, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (37, 9, 'patchy_fog', 0.9001, 77, 90, 1205, 687, 30, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (38, 9, 'patchy_fog', 0.8963, 77, 90, 1205, 687, 35, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (39, 9, 'patchy_fog', 0.9300, 127, 83, 1138, 673, 40, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (40, 9, 'patchy_fog', 0.9437, 1, 92, 1272, 690, 45, '2026-05-01 20:31:59');
INSERT INTO `detection_items` VALUES (41, 10, 'patchy_fog', 0.9694, 0, 45, 1279, 954, NULL, '2026-05-01 20:38:03');
INSERT INTO `detection_items` VALUES (43, 12, 'patchy_fog', 0.8745, 0, 103, 1273, 717, NULL, '2026-05-01 20:38:24');
INSERT INTO `detection_items` VALUES (44, 13, 'patchy_fog', 0.9589, 45, 92, 1207, 693, 0, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (45, 13, 'patchy_fog', 0.9586, 46, 92, 1208, 693, 5, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (46, 13, 'patchy_fog', 0.9609, 194, 89, 1080, 691, 10, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (47, 13, 'patchy_fog', 0.9708, 0, 94, 1272, 698, 15, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (48, 13, 'patchy_fog', 0.9707, 0, 94, 1272, 698, 20, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (49, 13, 'patchy_fog', 0.9591, 130, 90, 1133, 693, 25, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (50, 13, 'patchy_fog', 0.9001, 77, 90, 1205, 687, 30, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (51, 13, 'patchy_fog', 0.8963, 77, 90, 1205, 687, 35, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (52, 13, 'patchy_fog', 0.9300, 127, 83, 1138, 673, 40, '2026-05-01 20:38:31');
INSERT INTO `detection_items` VALUES (53, 13, 'patchy_fog', 0.9437, 1, 92, 1272, 690, 45, '2026-05-01 20:38:31');

-- ----------------------------
-- Table structure for detections
-- ----------------------------
DROP TABLE IF EXISTS `detections`;
CREATE TABLE `detections`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `source_type` enum('image','video','camera') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `original_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `input_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `output_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `output_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('success','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'success',
  `detect_count` int(11) NOT NULL DEFAULT 0,
  `confidence_avg` decimal(8, 4) NOT NULL DEFAULT 0.0000,
  `confidence_max` decimal(8, 4) NOT NULL DEFAULT 0.0000,
  `duration_ms` int(11) NOT NULL DEFAULT 0,
  `metadata` json NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_detections_user_time`(`user_id`, `created_at`) USING BTREE,
  INDEX `idx_detections_source_time`(`source_type`, `created_at`) USING BTREE,
  CONSTRAINT `fk_detections_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of detections
-- ----------------------------
INSERT INTO `detections` VALUES (2, 1, 'image', 'dawn_hf_mist-084.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\image\\c042b7f635c142e18e3b26818dcc640e.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\d0bd9dac2310433f97a6a0093afdc804.jpg', '/outputs/d0bd9dac2310433f97a6a0093afdc804.jpg', 'success', 1, 0.8487, 0.8487, 736, '{\"conf\": 0.25, \"width\": 512, \"height\": 302}', '2026-05-01 20:05:12');
INSERT INTO `detections` VALUES (3, 1, 'video', 'testimg_5s.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\video\\665d989ec15c4815bea9f846e7529151.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\6b9e407e0d7c49b7a92bca1084cd0533.webm', '/outputs/6b9e407e0d7c49b7a92bca1084cd0533.webm', 'success', 10, 0.9449, 0.9708, 1086, '{\"fps\": 10, \"conf\": 0.25, \"width\": 1280, \"frames\": 50, \"height\": 720, \"frame_step\": 5}', '2026-05-01 20:21:39');
INSERT INTO `detections` VALUES (5, 1, 'video', 'testimg_5s.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\video\\9f1ec7bb82e54791bf69d7b9372a8f18.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\e78c165a88c84316b5a4024dd03ff70c.webm', '/outputs/e78c165a88c84316b5a4024dd03ff70c.webm', 'success', 10, 0.9449, 0.9708, 1952, '{\"fps\": 10, \"conf\": 0.25, \"width\": 1280, \"frames\": 50, \"height\": 720, \"frame_step\": 5}', '2026-05-01 20:27:59');
INSERT INTO `detections` VALUES (6, 1, 'image', 'dawn_hf_foggy-026.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\image\\505e50e48dbb4ee3b6d491160de4ea97.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\4d1cd14ce79a4ae594783d0c58c23263.jpg', '/outputs/4d1cd14ce79a4ae594783d0c58c23263.jpg', 'success', 1, 0.9694, 0.9694, 775, '{\"conf\": 0.25, \"width\": 1280, \"height\": 960}', '2026-05-01 20:31:21');
INSERT INTO `detections` VALUES (7, 3, 'image', 'dawn_hf_foggy-008.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\image\\c251671cb4444874a7a1f48146702b25.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\af16e224ba8344189099a6d60748f750.jpg', '/outputs/af16e224ba8344189099a6d60748f750.jpg', 'success', 1, 0.9693, 0.9693, 36, '{\"conf\": 0.25, \"width\": 1280, \"height\": 726}', '2026-05-01 20:31:51');
INSERT INTO `detections` VALUES (9, 3, 'video', 'testimg_5s.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\video\\c8c02a0603894d108a042702a809f66c.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\a64d73ada4ab4fce9b39382b09d8f5db.webm', '/outputs/a64d73ada4ab4fce9b39382b09d8f5db.webm', 'success', 10, 0.9449, 0.9708, 1298, '{\"fps\": 10, \"conf\": 0.25, \"width\": 1280, \"frames\": 50, \"height\": 720, \"frame_step\": 5}', '2026-05-01 20:31:59');
INSERT INTO `detections` VALUES (10, 1, 'image', 'dawn_hf_foggy-026.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\image\\213f0d03ad564ca8bb9d82223db97301.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\9c27b515938c4ddfb2a0f3b331b3c7ce.jpg', '/outputs/9c27b515938c4ddfb2a0f3b331b3c7ce.jpg', 'success', 1, 0.9694, 0.9694, 819, '{\"conf\": 0.25, \"width\": 1280, \"height\": 960}', '2026-05-01 20:38:03');
INSERT INTO `detections` VALUES (12, 4, 'image', 'dawn_hf_foggy-050.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\image\\8b7d2304911947fab332838ab9b8cc89.jpg', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\aefb31266585422fb3a32170043e30de.jpg', '/outputs/aefb31266585422fb3a32170043e30de.jpg', 'success', 1, 0.8745, 0.8745, 33, '{\"conf\": 0.25, \"width\": 1280, \"height\": 755}', '2026-05-01 20:38:24');
INSERT INTO `detections` VALUES (13, 4, 'video', 'testimg_5s.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\uploads\\video\\066096bc27874c8aa03797745960e7e4.mp4', 'D:\\outproject_bak\\ByYOLOPatchyFogDetectionSystem\\outputs\\bb915471666448cb955ebe1607b8c2ad.webm', '/outputs/bb915471666448cb955ebe1607b8c2ad.webm', 'success', 10, 0.9449, 0.9708, 1298, '{\"fps\": 10, \"conf\": 0.25, \"width\": 1280, \"frames\": 50, \"height\": 720, \"frame_step\": 5}', '2026-05-01 20:38:31');

-- ----------------------------
-- Table structure for warning_alerts
-- ----------------------------
DROP TABLE IF EXISTS `warning_alerts`;
CREATE TABLE `warning_alerts`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NOT NULL,
  `detection_id` bigint(20) NULL DEFAULT NULL,
  `source_type` enum('image','video','camera') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `road_section` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `fog_level` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `visibility_level` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `speed_limit` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `snapshot_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `status` enum('active','handled') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_warning_user_time`(`user_id`, `created_at`) USING BTREE,
  INDEX `idx_warning_detection`(`detection_id`) USING BTREE,
  INDEX `idx_warning_source_time`(`source_type`, `created_at`) USING BTREE,
  CONSTRAINT `fk_warning_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `fk_warning_detection` FOREIGN KEY (`detection_id`) REFERENCES `detections` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of warning_alerts
-- ----------------------------

-- ----------------------------
-- Table structure for system_events
-- ----------------------------
DROP TABLE IF EXISTS `system_events`;
CREATE TABLE `system_events`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) NULL DEFAULT NULL,
  `event_type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_events_time`(`created_at`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_events
-- ----------------------------
INSERT INTO `system_events` VALUES (1, NULL, 'database_init', 'database initialized', '2026-05-01 19:53:25');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT '',
  `role` enum('admin','user') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user',
  `status` enum('active','disabled') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `last_login` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------

-- ----------------------------
-- Table structure for sms_logs
-- ----------------------------
DROP TABLE IF EXISTS `sms_logs`;
CREATE TABLE `sms_logs`  (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `warning_id` bigint(20) NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('pending','success','failed') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `error_message` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `sent_at` datetime NULL DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_sms_warning`(`warning_id`) USING BTREE,
  INDEX `idx_sms_phone_time`(`phone`, `created_at`) USING BTREE,
  CONSTRAINT `fk_sms_warning` FOREIGN KEY (`warning_id`) REFERENCES `warning_alerts` (`id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;



INSERT INTO `users` VALUES (1, 'admin', 'scrypt:32768:8:1$IC3Ul7SE3XjA9KaH$4c4791e82737c8fb927cdabbb5bc724f13d7f7d52c37881bbf287c2d6b0bf4e9b3997ce97c38cdc14e4b344bd45b60c8845885ea686bff6460200d51dd454f5a', '系统管理员', 'admin', 'active', '2026-05-01 19:53:25', '2026-05-01 20:38:57', '2026-05-01 20:38:57');
INSERT INTO `users` VALUES (2, 'operator', 'scrypt:32768:8:1$y1gl8exwKCwFCvE5$7032e25dfe79ca4b03aa32ac91234e0074ed225e8df1e675bcf8b8818cf1915037e03ad657d421be668c73ee912b75b5e5cdf56aa453826c6a178cb18e3eaab0', '检测员', 'user', 'active', '2026-05-01 19:53:25', '2026-05-01 19:53:25', NULL);
INSERT INTO `users` VALUES (3, 'test', 'scrypt:32768:8:1$Hk81mQdQBaK7dMYm$3f955fa153cf8cf05799f8f6426208a56f6c66de9bd897490463690e1524ca16c29dbc313ff16799f05b1e256c4306b9c75e3927fb9ea8905e094aeced275ce2', 'test1', 'user', 'active', '2026-05-01 20:31:46', '2026-05-01 20:39:05', NULL);
INSERT INTO `users` VALUES (4, 'test1', 'scrypt:32768:8:1$Ro4APi4CyJ1BeMb1$7b94e22720699174950b238d0366997000751e6edbc49c93bd5bee54a81de513a45df83df94ddb85562f4d30c2cc8e9925914fd35caae24e43edf3e5f0f04bc8', '1321', 'user', 'active', '2026-05-01 20:38:17', '2026-05-01 20:38:17', NULL);

SET FOREIGN_KEY_CHECKS = 1;
