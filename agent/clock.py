from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
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


engine_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(USER, PW, HOST, PORT, NAME) 

ssl_args = {"sslmode": "require", "sslrootcert": SSL_PATH}


jobstores = {'default': SQLAlchemyJobStore(url=engine_string)}
executors = {'default': ThreadPoolExecutor(2)}
job_defaults = {'coalesce': False, 'max_instances':1}

sched = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc, engine_options=ssl_args)
logging.basicConfig(filename='dailyUpdateLog.txt', level=logging.DEBUG)
