from chi311_import import historicals, check_updates, dedupe_df, update_table
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import get_key, find_dotenv
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

job_defaults = {'coalesce': True, 'misfire_grace_time': 20}


logging.basicConfig(filename='dailyUpdateLog.txt', level=logging.DEBUG)


if __name__ == '__main__':
    scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults=job_defaults, timezone=utc, engine_options=ssl_args, jitter=30)

    def daily_db_update(historicals_list, days_back = 1): 
        try:
            for service_dict in historicals_list:
                print("starting {}...".format(service_dict['service_name']))
                updated = check_updates(service_dict, days_back)
                clean_updates = dedupe_df(updated, service_dict)
                update_table(clean_updates, service_dict['service_name'])
                logging.info("completed without error at {}.".format(datetime.now()))
        except Exception as e:
            logging.info("Encountered error: {} at {}.".format(e, datetime.now()))
        

    job = scheduler.add_job(daily_db_update, 'cron', day_of_week='0-6', hour=6, minute=42, args=[historicals])
    scheduler.start()
