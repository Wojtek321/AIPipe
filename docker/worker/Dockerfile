FROM python:3.12-alpine

COPY ../worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ../worker /worker

CMD ["celery", "-A", "worker", "worker", "--loglevel=info"]
