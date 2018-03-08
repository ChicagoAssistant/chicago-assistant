from chi311_import import historicals, check_updates, dedupe_df, update_table
from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import utc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import get_key, find_dotenv
import os

USER = os.environ['DB_USER']
NAME = os.environ['DB_NAME']
PW = os.environ['DB_PW']
HOST = os.environ['DB_HOST']
PORT = os.environ['DB_PORT']
SSL_DIR = os.path.dirname(__file__)
SSL = os.environ['SSL']
SSL_PATH = os.path.join(SSL_DIR, SSL)

engine_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(USER, PW, HOST, PORT, NAME) 
ssl_args = {"sslmode": "require", "sslrootcert": SSL_PATH}

jobstores = {
    'default': SQLAlchemyJobStore(url=engine_string)
}

job_defaults = {
    'coalesce': True,
    'misfire_grace_time': 12
}

sched = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults, timezone=utc, engine_options=ssl_args)


# @sched.scheduled_job('cron', day_of_week='0-6', hour=11, minute=6, args=[historicals])
# def daily_db_update(historicals_list, days_back = 1): 
#     # add error flag, maybe trigger email?
#     all_updates = []
#     try:
#         for service_dict in historicals_list:
#             print("starting {}...".format(service_dict['service_name']))
#             updated = check_updates(service_dict, days_back)
#             clean_updates = dedupe_df(updated, service_dict)
#             update_table(clean_updates, service_dict['service_name'])
#         return "completed without error"
#     except Exception as e:
#         print("Update failed: {}".format(e))

# sched.start()


def daily_db_update(historicals_list, days_back = 1): 
    try:
        for service_dict in historicals_list:
            print("starting {}...".format(service_dict['service_name']))
            updated = check_updates(service_dict, days_back)
            clean_updates = dedupe_df(updated, service_dict)
            update_table(clean_updates, service_dict['service_name'])
            print("completed without error")
    except Exception as e:
        print("Update failed: {}".format(e))

# job = sched.add_cron_job(daily_db_update, day_of_week='0-6', hour=11, minute=6, args=[historicals])
job = sched.add_job(daily_db_update, 'cron', day_of_week='0-6', hour=12, minute=3, args=[historicals])

sched.start()
