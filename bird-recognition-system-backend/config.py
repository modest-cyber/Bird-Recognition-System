import os
from datetime import timedelta

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# ==================== 数据库配置 ====================
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "bird_recognition")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

# ==================== Redis 配置 ====================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# ==================== JWT 配置 ====================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "bird-recognition-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_DAYS = 7
JWT_ACCESS_TOKEN_EXPIRE = timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)

# ==================== YOLO 配置 ====================
YOLO_LOCAL_SOURCE_DIR = os.path.join(PROJECT_ROOT, "ultralytics-main")
YOLO_DEFAULT_WEIGHTS_PATH = os.path.join(BASE_DIR, "yolo", "weights", "bird_model.pt")
YOLO_DATASET_WEIGHTS_PATH = os.path.join(PROJECT_ROOT, "yolov8-bird", "best.pt")
YOLO_WEIGHTS_CANDIDATES = [
    os.getenv("YOLO_WEIGHTS_PATH"),
    YOLO_DEFAULT_WEIGHTS_PATH,
    YOLO_DATASET_WEIGHTS_PATH,
]


def resolve_yolo_weights_path() -> str:
    """返回当前应使用的 YOLO 权重路径。"""
    for candidate in YOLO_WEIGHTS_CANDIDATES:
        if candidate and os.path.exists(candidate):
            return candidate
    return YOLO_DEFAULT_WEIGHTS_PATH


YOLO_WEIGHTS_PATH = resolve_yolo_weights_path()
YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", 0.4))

# ==================== 数据集配置 ====================
DATASET_DIR = os.path.join(BASE_DIR, "datasets")
DATASET_IMAGES_DIR = os.path.join(DATASET_DIR, "images")
DATASET_LABELS_DIR = os.path.join(DATASET_DIR, "labels")
DATASET_CLASSES_FILE = os.path.join(DATASET_DIR, "classes.txt")

# ==================== 训练配置 ====================
TRAINING_OUTPUT_DIR = os.path.join(BASE_DIR, "training_output")
DEFAULT_EPOCHS = 100
DEFAULT_BATCH_SIZE = 16
DEFAULT_LEARNING_RATE = 0.01
DEFAULT_VAL_SPLIT = 0.2
DEFAULT_IMG_SIZE = 640

# ==================== 文件上传配置 ====================
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
UPLOAD_ORIGINAL_DIR = os.path.join(UPLOAD_DIR, "original")
UPLOAD_ANNOTATED_DIR = os.path.join(UPLOAD_DIR, "annotated")
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

# ==================== 缓存配置 ====================
CACHE_BIRD_LIST_TTL = 600
CACHE_ADMIN_STATS_TTL = 300

# ==================== CORS 配置 ====================
CORS_ORIGINS = ["*"]

# ==================== 分页默认配置 ====================
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
