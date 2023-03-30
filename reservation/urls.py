from django.urls import path, include
from reservation import views
from rest_framework_nested import routers

# Use drf nested router to register view set routes
router = routers.DefaultRouter()
router.register('properties', views.PropertyViewSet, basename='properties')

urlpatterns = [
    path('', include(router.urls)),

]
