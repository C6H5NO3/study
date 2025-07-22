import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from scrapy import cmdline

def job_func():
    os.chdir(os.path.dirname(__file__))
    cmdline.execute(f"scrapy crawl spider -o {datetime.now().date()}.json".split())

scheduler = BackgroundScheduler()
scheduler.add_job(job_func, 'cron', hour=0, minute=1)  # Runs daily at midnight
scheduler.start()

input("Press Enter to exit...\n")