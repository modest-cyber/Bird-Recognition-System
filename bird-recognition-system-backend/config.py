"""
鸟类识别系统 - 配置文件
包含数据库、Redis、JWT 等配置
"""
import os
from datetime import timedelta

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)  # Redis 默认无密码
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# ==================== JWT 配置 ====================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "bird-recognition-secret-key-2026")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_DAYS = 7
JWT_ACCESS_TOKEN_EXPIRE = timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)

# ==================== YOLO 配置 ====================
YOLO_WEIGHTS_PATH = os.path.join(BASE_DIR, "yolo", "weights", "bird_model.pt")
YOLO_CONFIDENCE_THRESHOLD = 0.4

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
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

# ==================== 缓存配置 ====================
CACHE_BIRD_LIST_TTL = 600  # 鸟类列表缓存 10 分钟
CACHE_ADMIN_STATS_TTL = 300  # 统计数据缓存 5 分钟

# ==================== CORS 配置 ====================
CORS_ORIGINS = ["*"]  # 允许所有来源

# ==================== 分页默认配置 ====================
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
