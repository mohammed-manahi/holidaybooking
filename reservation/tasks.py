from celery import shared_task
from django.utils import timezone
from reservation.models import Reservation


@shared_task
def update_reservation_state():
    """
    Create a celery cron job to monitor reservation state of a reserved property
    """
    now = timezone.now()
    for reservation in Reservation.objects.all():
        if reservation.reservation_from <= now <= reservation.reservation_to:
            reservation.reserved = True
        else:
            reservation.reserved = False
        reservation.save()
