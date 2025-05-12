FROM python:3.12-alpine

ENV PYTHONPATH=/project

WORKDIR /project

COPY ../app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../app ./app
COPY ../worker ./worker

EXPOSE 8000

CMD ["python", "app/src/main.py"]
