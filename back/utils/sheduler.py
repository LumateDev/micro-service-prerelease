from apscheduler.schedulers.background import BackgroundScheduler
from services.cron_jobs import get_last_5_users, cleanup_old_sessions, send_daily_notifications

scheduler = BackgroundScheduler()

scheduler.add_job(get_last_5_users, 'cron', hour=8, minute=0)
scheduler.add_job(send_daily_notifications, 'cron', hour=9, minute=0)
scheduler.add_job(cleanup_old_sessions, 'cron', hour=10, minute=0)

def start_scheduler():
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()