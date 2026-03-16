"""
鸟类识别系统 - 数据库连接和 Session 管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

from config import (
    DATABASE_URL,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB
)

# ==================== MySQL 数据库连接 ====================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """获取数据库 Session 依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Redis 连接 ====================
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
    decode_responses=True
)


def get_redis():
    """获取 Redis 客户端依赖"""
    return redis_client


def check_redis_connection():
    """检查 Redis 连接状态"""
    try:
        redis_client.ping()
        return True
    except redis.ConnectionError:
        return False
