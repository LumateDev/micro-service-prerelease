from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User, Session
from datetime import datetime, timedelta
from services.notifications import send_notification

async def get_last_5_users():
    async with get_db() as db:
        result = await db.execute(select(User).order_by(User.created_at.desc()).limit(5))
        users = result.scalars().all()
        print(f"Последние 5 пользователей: {[user.email for user in users]}")

async def cleanup_old_sessions():
    async with get_db() as db:
        threshold = datetime.now() - timedelta(days=30)
        await db.execute(delete(Session).where(Session.created_at < threshold))
        await db.commit()
    print("Устаревшие сессии удалены!")

def send_daily_notifications():
    send_notification("Привет! У нас есть новые функции в системе. Проверьте их!")