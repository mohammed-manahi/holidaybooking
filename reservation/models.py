from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Property(models.Model):
    """
    Create property model
    """
    # Define cancellation policy choices
    FREE_CANCELLATION = 'Free Cancellation'
    PAID_CANCELLATION = 'Paid Cancellation'
    CANCELLATION_POLICY_CHOICES = [
        (FREE_CANCELLATION, FREE_CANCELLATION),
        (PAID_CANCELLATION, PAID_CANCELLATION)
    ]
    name = models.CharField(max_length=250, blank=False)
    description = models.TextField(max_length=500)
    slug = models.SlugField(max_length=250, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    address = models.CharField(max_length=500)
    size = models.FloatField()
    # Use postgis for property location
    location = models.PointField(geography=True, default=Point(0.0, 0.0))
    number_of_bedrooms = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    number_of_beds = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    number_of_baths = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    number_of_adult_guests = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    number_of_child_guests = models.PositiveSmallIntegerField(validators=[MinValueValidator(0)])
    price_per_night = models.DecimalField(max_digits=6, decimal_places=2)
    deposit = models.DecimalField(max_digits=4, decimal_places=2)
    available = models.BooleanField()
    available_from = models.DateTimeField()
    available_to = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_policy = models.CharField(max_length=25, choices=CANCELLATION_POLICY_CHOICES,
                                           default=FREE_CANCELLATION)
    cancellation_fee_per_night = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta():
        # Define meta attributes
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def save(self, *args, **kwargs):
        # Override save method to automatically assign the slug field based on the property name using slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
