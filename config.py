import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Tuple

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = os.getenv("FOG_DB_HOST", "127.0.0.1")
    port: int = int(os.getenv("FOG_DB_PORT", "3307"))
    user: str = os.getenv("FOG_DB_USER", "root")
    password: str = os.getenv("FOG_DB_PASSWORD", "123456")
    name: str = os.getenv("FOG_DB_NAME", "patchy_fog_system")
    pool_size: int = int(os.getenv("FOG_DB_POOL_SIZE", "5"))
    pool_name: str = "fog_detection_pool"

    @property
    def dsn(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "database": self.name,
        }


@dataclass(frozen=True)
class JWTConfig:
    secret: str = os.getenv("FOG_JWT_SECRET", "patchy-fog-system-secret")
    algorithm: str = "HS256"
    expiry_hours: int = int(os.getenv("FOG_JWT_EXPIRY_HOURS", "12"))


@dataclass(frozen=True)
class SMSConfig:
    provider: str = os.getenv("SMS_PROVIDER", "ihuyi")
    sign_name: str = os.getenv("SMS_SIGN_NAME", "Patchy Fog Warning System")
    ihuyi_account: str = os.getenv("IHUYI_ACCOUNT", "")
    ihuyi_password: str = os.getenv("IHUYI_PASSWORD", "")
    ihuyi_url: str = os.getenv("IHUYI_URL", "https://api.ihuyi.com/sms/Submit.json")
    aliyun_key_id: str = os.getenv("SMS_ACCESS_KEY_ID", "")
    aliyun_key_secret: str = os.getenv("SMS_ACCESS_KEY_SECRET", "")
    template_code: str = os.getenv("SMS_TEMPLATE_CODE", "")


@dataclass(frozen=True)
class ModelConfig:
    confidence_default: float = 0.25
    imgsz: int = 640
    frame_step_default: int = 5
    frame_step_max: int = 30
    detection_limit: int = 1000

    @property
    def image_exts(self) -> Set[str]:
        return {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    @property
    def video_exts(self) -> Set[str]:
        return {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm"}

    @property
    def training_charts(self) -> list:
        return [
            ("results.png", "Training Results"),
            ("F1_curve.png", "F1 Curve"),
            ("P_curve.png", "P Curve"),
            ("PR_curve.png", "PR Curve"),
            ("R_curve.png", "R Curve"),
        ]


@dataclass(frozen=True)
class RateLimitConfig:
    default: str = os.getenv("FOG_RATE_LIMIT_DEFAULT", "100 per minute")
    detect_image: str = os.getenv("FOG_RATE_LIMIT_DETECT_IMAGE", "30 per minute")
    detect_video: str = os.getenv("FOG_RATE_LIMIT_DETECT_VIDEO", "10 per minute")
    auth: str = os.getenv("FOG_RATE_LIMIT_AUTH", "20 per minute")


@dataclass
class AppConfig:
    """Application config aggregating all sub-configs."""
    root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 5001
    max_content_mb: int = 600

    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    jwt: JWTConfig = field(default_factory=JWTConfig)
    sms: SMSConfig = field(default_factory=SMSConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

    @property
    def max_content_length(self) -> int:
        return self.max_content_mb * 1024 * 1024

    @property
    def upload_dir(self) -> Path:
        return self.root / "uploads"

    @property
    def output_dir(self) -> Path:
        return self.root / "outputs"

    @property
    def log_dir(self) -> Path:
        return self.root / "logs"

    @property
    def frontend_dist(self) -> Path:
        return self.root / "frontend" / "dist"

    @property
    def model_path(self) -> Path:
        path = self.root / "runs" / "detect" / "patchy_fog_yolov8n" / "weights" / "best.pt"
        return path if path.exists() else self.root / "yolov8n.pt"

    @property
    def train_run_dir(self) -> Path:
        return self.root / "runs" / "detect" / "patchy_fog_yolov8n"


config = AppConfig()

