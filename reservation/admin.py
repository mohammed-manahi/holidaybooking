from django.contrib import admin
from reservation.models import Property, Media, Feature, FeatureCategory, Review, Category, Reservation


@admin.register(Media)
class PropertyMedia(admin.ModelAdmin):
    """
    Register property media model in admin site
    """
    list_display = ['name', 'property']
    list_filter = ['property']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """
    Register property model in admin site
    """
    list_display = ['name', 'description', 'owner', 'address', 'available']
    list_filter = ['category', 'available']


@admin.register(FeatureCategory)
class PropertyFeatureCategoryAdmin(admin.ModelAdmin):
    """
    Add property media model in admin site
    """
    list_display = ['name', 'description']
    list_filter = ['name']


@admin.register(Feature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    """
    Add property media model in admin site
    """
    list_display = ['name', 'description']
    list_filter = ['name']


@admin.register(Review)
class PropertyReviewAdmin(admin.ModelAdmin):
    """
    Add property review model in admin site
    """
    list_display = ['user', 'property', 'rate']
    list_filter = ['rate']


@admin.register(Category)
class PropertyCategoryAdmin(admin.ModelAdmin):
    """
    Add property review model in admin site
    """
    list_display = ['name', 'description', 'slug']
    list_filter = ['name']


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['property', 'reservation_from', 'reservation_to', 'reservation_to', 'guest']
    list_filter = ['guest', 'property']
