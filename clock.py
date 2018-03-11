from chi311_import import historicals, check_updates, dedupe_df, update_table
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from dotenv import get_key, find_dotenv
from datetime import datetime
import os
import logging


USER = os.environ['DB_USER']
NAME = os.environ['DB_NAME']
PW = os.environ['DB_PW']
HOST = os.environ['DB_HOST']
PORT = os.environ['DB_PORT']
SSL_DIR = os.path.dirname(__file__)
SSL = os.environ['SSL']
SSL_PATH = os.path.join(SSL_DIR, SSL)

# USER = get_key(find_dotenv(), 'DB_USER')
# NAME = get_key(find_dotenv(), 'DB_NAME')
# PW = get_key(find_dotenv(), 'DB_PW')
# HOST = get_key(find_dotenv(), 'DB_HOST')
# PORT = get_key(find_dotenv(), 'DB_PORT')
# SSL = get_key(find_dotenv(), 'SSL')
# SSL_DIR = os.path.dirname(__file__)
# SSL_PATH = os.path.join(SSL_DIR, SSL)

engine_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(USER, PW, HOST, PORT, NAME) 

ssl_args = {"sslmode": "require", "sslrootcert": SSL_PATH}

jobstores = {'default': SQLAlchemyJobStore(url=engine_string)}
job_defaults = {'coalesce': True, 'max_instances':1}

sched = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults, timezone=utc, engine_options=ssl_args)
logging.basicConfig(filename='dailyUpdateLog.txt', level=logging.INFO)


# class ScheduledJobConfigs(object):
#     job_id = 1
#     JOBS = [
#         {
#             'id': job_id + 1,
#             'func': 'chi311_import:daily_db_update',
#             'args': (historicals),
#             'trigger': 'cron',
#             'day_of_week': '0-6',
#             'hour': '19',
#             'minute': '8',
#             'jitter': '10',
#         },
#     ]

update_job_id = 0

# @sched.scheduled_job('cron', id=update_job_id, day_of_week='0-6', hour=22, minute=18, args=[historicals], jitter=30)
def daily_db_update(historicals_list, days_back = 1): 
    for service_dict in historicals_list:            
        updated = check_updates(service_dict, days_back)
        clean_updates = dedupe_df(updated, service_dict)
        update_table(clean_updates, service_dict['service_name'])

    update_job_id += 1

# scheduler.add_job(daily_db_update, 'interval', minutes=2)

sched.add_job(daily_db_update, 'cron', day_of_week='0-6', hour=3, minute=10, args=[historicals])

sched.start()
