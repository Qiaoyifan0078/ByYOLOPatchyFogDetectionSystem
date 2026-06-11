# 🚗 团雾识别检测系统 — ByYOLOPatchyFogDetectionSystem

> **YOLOv8 驱动的智能团雾检测与预警平台**  
> 支持图片/视频/摄像头实时检测 · 自动分级预警 · 可视化大屏监控

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue" />
  <img src="https://img.shields.io/badge/PyTorch-2.4-red" />
  <img src="https://img.shields.io/badge/YOLOv8-nano-green" />
  <img src="https://img.shields.io/badge/Flask-3.0-lightgrey" />
  <img src="https://img.shields.io/badge/Vue-2.7-brightgreen" />
  <img src="https://img.shields.io/badge/license-MIT-blue" />
</p>

---

## ✨ 系统亮点

| 特性 | 说明 |
|------|------|
| 🎯 **精准检测** | 基于 YOLOv8n 模型，针对团雾（Patchy Fog）场景专项训练，支持自定义置信度阈值 |
| 🖼️ **多模态输入** | 支持图片（JPG/PNG/WEBP）、视频（MP4/AVI/MOV）、摄像头实时截帧三种识别模式 |
| 🧠 **智能分级预警** | 根据检测目标数量 + 置信度自动判断团雾等级（轻度/中度/重度/特重）、推算能见度、给出限速建议 |
| 📊 **可视化大屏** | 暗色科技风 Dashboard，实时展示预警总数、团雾等级分布柱状图、识别时间线，支持今日/本周/本月时间筛选 |
| 📱 **短信通知** | 预警发布后自动发送短信，支持互亿无线/阿里云/腾讯云三大短信服务商 |
| 🔐 **权限管理** | 管理员/检测员双角色，JWT 认证，接口级权限控制 |
| 🏗️ **生产级架构** | Flask Blueprint 模块化、MySQL 连接池、结构化日志（JSON 轮转）、健康检查 + Prometheus 指标、安全头中间件 |
| 🎨 **专业 UI** | 浅色专业风格后台 + 暗色科技风大屏，响应式布局，支持 PC/平板 |

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+（端口 3307）
- Node.js 16+（前端构建）
- CUDA 11.8+（GPU 推理，可选）

### 1. 安装依赖

```powershell
cd ByYOLOPatchyFogDetectionSystem
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. 初始化数据库

```powershell
.\.venv\Scripts\python.exe init_db.py
```

默认创建管理员账号 `admin / 123456` 和操作员账号 `operator / 123456`。

### 3. 启动后端

```powershell
.\.venv\Scripts\python.exe app.py
```

服务运行在 `http://127.0.0.1:5001`，启动时自动检测 GPU、预热 YOLO 模型。

### 4. 构建前端（可选）

前端已内置编译产物。如需修改前端后重新构建：

```powershell
cd frontend
npm install
npm run build
```

---

## 📁 项目结构

```
ByYOLOPatchyFogDetectionSystem/
├── app.py                 # Flask 入口（中间件、静态服务）
├── config.py              # 集中配置管理（dataclass）
├── api/                   # Blueprint 路由模块
│   ├── auth.py            #   认证（注册/登录）
│   ├── detect.py          #   检测（图片/视频 + 历史记录）
│   ├── warnings.py        #   预警（CRUD + 短信通知）
│   ├── admin.py           #   管理员（用户管理）
│   └── system.py          #   系统（训练统计 / 健康检查 / 指标）
├── utils/                 # 工具模块
│   ├── logging_config.py  #   结构化日志（JSON 轮转）
│   ├── errors.py          #   自定义异常 + 全局错误处理
│   └── response.py        #   标准化 API 响应
├── sms_service.py         # 短信服务（互亿/阿里云/腾讯云）
├── scripts/
│   └── train_yolov8_patchy_fog.py  # 模型训练脚本
├── frontend/              # Vue 2 前端
│   └── src/
│       ├── pages/         #   页面组件
│       │   ├── Dashboard.vue      # 可视化大屏
│       │   ├── ImageDetect.vue    # 图片识别
│       │   ├── VideoDetect.vue    # 视频识别
│       │   ├── CameraDetect.vue   # 摄像头识别
│       │   └── ...
│       └── components/    #   通用组件
├── runs/                  # 训练产物（模型权重、评估图表）
├── patchy_fog_system.sql  # 数据库建表 SQL
└── requirements.txt       # Python 依赖
```

---

## 🔧 配置说明

复制 `env.example.env` 为 `.env`，按需修改：

```env
# 数据库
FOG_DB_HOST=127.0.0.1
FOG_DB_PORT=3307
FOG_DB_USER=root
FOG_DB_PASSWORD=123456
FOG_DB_NAME=patchy_fog_system

# JWT
FOG_JWT_SECRET=your-secret-key

# 短信服务（可选）
SMS_PROVIDER=ihuyi           # ihuyi / aliyun / tencent
IHUYI_ACCOUNT=your_account
IHUYI_PASSWORD=your_password
```

---

## 🧪 模型训练

```powershell
.\.venv\Scripts\python.exe scripts\train_yolov8_patchy_fog.py \
    --model yolov8n.pt \
    --epochs 30 \
    --batch 8 \
    --device 0
```

训练完成后，图表和权重保存在 `runs/detect/patchy_fog_yolov8n/`。

---

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| POST | `/api/auth/register` | 注册 |
| GET | `/api/auth/me` | 当前用户信息 |
| POST | `/api/detect/image` | 图片识别 |
| POST | `/api/detect/video` | 视频识别 |
| GET | `/api/detections` | 历史记录列表 |
| DELETE | `/api/detections/:id` | 删除记录 |
| GET/POST | `/api/warnings` | 预警列表 / 发布预警 |
| DELETE | `/api/warnings/:id` | 删除预警 |
| GET | `/api/training/stats` | 训练统计 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/metrics` | Prometheus 指标 |

---

## 📸 系统截图

### 登录页
![登录](img.png)

### 可视化大屏
> 暗色科技风 Dashboard，实时数据卡片、团雾等级分布、识别时间线

### 图片识别
> 拖拽上传 + 置信度调节 + 检测框标注 + 结果统计

### 预警发布
> 自动分析团雾等级/能见度/限速建议，一键发布 + 短信通知

---

## 📄 License

MIT License