broker_url = 'pyamqp://guest@rabbitmq//'

result_backend = 'redis://redis:6379/0'
result_expires = 3600

imports = ['worker.tasks']
