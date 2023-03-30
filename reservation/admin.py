from django.contrib import admin
from reservation.models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    Register property model in admin site
    """
    list_display = ['name', 'description', 'owner', 'address', 'available']
    list_filter = ['available']
