from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from reservation.models import Reservation
from django.conf import settings


@receiver(post_save, sender=Reservation)
def change_reservation_status_on_create(sender, instance, created, **kwargs):
    """
    Create a signal to change reservation state (reserved boolean field) to true when a reservation instance is made
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        instance.reserved = True
        instance.save()


# @receiver(post_save, sender=Reservation)
# def change_reservation_status_on_date_duration(sender, instance, created, **kwargs):
#     """
#     Create a signal to change the reservation state (reserved boolean field) based on checking reservation dates
#     :param created:
#     :param sender:
#     :param instance:
#     :param kwargs:
#     :return:
#     """
#     if created:
#         time_now = timezone.now()
#         if instance.reservation_from <= time_now <= instance.reservation_to:
#             instance.reserved = True
#         else:
#             instance.reserved = False
#         instance.save()
