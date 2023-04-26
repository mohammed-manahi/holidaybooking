import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holidaybooking.settings')

app = Celery('holidaybooking')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'update-reservation-state': {
        'task': 'reservation.tasks.update_reservation_state',
        'schedule': crontab(),  # run every minute
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
