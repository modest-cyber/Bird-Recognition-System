"""
管理员服务 - 统计数据、用户管理
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import redis_client
from models.user import User
from models.record import Record
from config import CACHE_ADMIN_STATS_TTL


class AdminService:
    """管理员服务类"""
    
    @staticmethod
    def get_stats(db: Session) -> Dict:
        """获取系统统计数据"""
        # 尝试从缓存获取
        cache_key = "cache:admin:stats"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 用户总数
        total_users = db.query(User).count()
        
        # 识别记录总数
        total_records = db.query(Record).count()
        
        # 今日识别记录数
        today = datetime.now().date()
        today_records = db.query(Record).filter(
            func.date(Record.created_at) == today
        ).count()
        
        # 鸟类识别排行（从记录的 result_json 中统计）
        bird_rank = AdminService._get_bird_rank(db)
        
        # 近 7 天每日识别趋势
        daily_trend = AdminService._get_daily_trend(db)
        
        stats = {
            "total_users": total_users,
            "total_records": total_records,
            "today_records": today_records,
            "bird_rank": bird_rank,
            "daily_trend": daily_trend
        }
        
        # 缓存结果
        redis_client.setex(cache_key, CACHE_ADMIN_STATS_TTL, json.dumps(stats))
        
        return stats
    
    @staticmethod
    def _get_bird_rank(db: Session, limit: int = 10) -> List[Dict]:
        """获取鸟类识别排行"""
        # 获取所有记录的识别结果
        records = db.query(Record.result_json).all()
        
        # 统计每种鸟类的出现次数
        bird_count = {}
        for record in records:
            results = record[0]
            if isinstance(results, list):
                for result in results:
                    if isinstance(result, dict):
                        bird_name = result.get("bird_name", "未知")
                        bird_count[bird_name] = bird_count.get(bird_name, 0) + 1
        
        # 排序并取前 N 个
        sorted_birds = sorted(bird_count.items(), key=lambda x: x[1], reverse=True)
        return [{"bird_name": name, "count": count} for name, count in sorted_birds[:limit]]
    
    @staticmethod
    def _get_daily_trend(db: Session, days: int = 7) -> List[Dict]:
        """获取近 N 天每日识别趋势"""
        trend = []
        today = datetime.now().date()
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            count = db.query(Record).filter(
                func.date(Record.created_at) == date
            ).count()
            trend.append({
                "date": date.strftime("%Y-%m-%d"),
                "count": count
            })
        
        return trend
    
    @staticmethod
    def clear_stats_cache():
        """清除统计缓存"""
        redis_client.delete("cache:admin:stats")
