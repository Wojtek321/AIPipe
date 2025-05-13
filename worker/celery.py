from celery import Celery
from worker import celeryconfig


app = Celery(__name__)
app.config_from_object(celeryconfig)
