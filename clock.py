from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week=0-6, hour=4, minute=12)
def scheduled_job():
    print('This job is run every weekday at 5pm.')

sched.start()