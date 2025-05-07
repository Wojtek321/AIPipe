from celery import Celery


app = Celery(__name__,
             broker='pyamqp://guest@rabbitmq//',
             backend='redis://redis:6379/0',
             include=['worker.tasks'])

app.conf.update(
    result_expires=3600,
)
