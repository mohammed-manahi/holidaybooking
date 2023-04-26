import json
import os
import requests
from decimal import Decimal
from django.db.models.aggregates import Avg
from django.utils import timezone
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from reservation.models import Property, Category, Media, Feature, FeatureCategory, Review, Reservation
from django.contrib.gis.geoip2 import GeoIP2


class MediaSerializer(serializers.ModelSerializer):
    """
    Create serializer for media model
    """

    class Meta():
        model = Media
        fields = ['id', 'name', 'description', 'photo', 'video', 'user']

        # Get current authenticated user

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        """
        Custom validation to allow owner only to add media to property
        :param attrs:
        :return:
        """
        property_id = self.context['property_id']
        user = self.context['request'].user
        if not Media.objects.filter(property_id=property_id, property__owner_id=user.id):
            raise serializers.ValidationError('Only property owner can add media to their own property')
        return attrs

    def create(self, validated_data):
        """
        Override create method to allow nested route for media in property api endpoint
        :param validated_data:
        :return:
        """
        property_id = self.context['property_id']
        return Media.objects.create(property_id=property_id, **validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Create serializer for review model
    """
    # Get current authenticated user
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta():
        model = Review
        fields = ['id', 'comment', 'rate', 'user']

    def validate(self, attrs):
        """
        Custom validation to allow user review a property once only
        :param attrs:
        :return:
        """
        property_id = self.context['property_id']
        user = attrs['user']
        if Review.objects.filter(property_id=property_id, user=user).exists():
            raise serializers.ValidationError('You have already reviewed this property')
        return attrs

    def create(self, validated_data):
        """
        Override create method to allow nested route for review in property api endpoint
        :param validated_data:
        :return:
        """
        property_id = self.context['property_id']
        return Review.objects.create(property_id=property_id, **validated_data)


class FeatureCategorySerializer(serializers.ModelSerializer):
    """
    Create serializer for feature category model
    """

    class Meta():
        model = FeatureCategory
        fields = ['id', 'name', 'description', 'slug']


class FeatureSerializer(serializers.ModelSerializer):
    """
    Create serializer for feature model
    """

    class Meta():
        model = Feature
        fields = ['id', 'name', 'description', 'feature_category']

    def create(self, validated_data):
        """
        Override create method to allow nested route for feature in property api endpoint
        :param validated_data:
        :return:
        """
        property_id = self.context['property_id']
        return Feature.objects.create(property_id=property_id, **validated_data)


class CategorySerializer(serializers.ModelSerializer):
    """
    Create serializer for category model
    """

    class Meta():
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'property_count']

    # Custom field that calls get property category method
    property_count = serializers.SerializerMethodField(method_name='get_property_count')

    def get_property_count(self, property_category):
        # Custom method to get number of properties in a category
        return property_category.properties.count()


class PropertySerializer(serializers.ModelSerializer):
    """
    Create serializer for property model
    """
    # Get current authenticated user
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available = serializers.BooleanField(default=True, read_only=True)

    def validate(self, attrs):
        """
        Custom validation for available from and available to fields
        :param attrs:
        :return:
        """
        if attrs['available_from'] > attrs['available_to']:
            raise serializers.ValidationError('Available to date must occur after available from date')
        if not attrs['available_from'] >= timezone.now() <= attrs['available_to']:
            raise serializers.ValidationError('Availability dates are not valid')
        return attrs

    class Meta():
        model = Property
        fields = ['id', 'name', 'description', 'slug', 'owner', 'category', 'address', 'size', 'location',
                  'number_of_bedrooms', 'number_of_beds', 'number_of_baths', 'number_of_adult_guests',
                  'number_of_child_guests', 'price_per_night', 'available_from', 'available_to',
                  'cancellation_policy', 'cancellation_fee_per_night', 'media', 'reviews', 'features', 'available',
                  'average_rate']
        read_only_fields = ['available']

    # Display property media
    media = MediaSerializer(many=True, read_only=True)

    # Display property reviews
    reviews = ReviewSerializer(many=True, read_only=True)

    # Display property features
    features = FeatureSerializer(many=True, read_only=True)

    # Custom field for average review rate
    average_rate = serializers.SerializerMethodField(method_name='get_average_rate')

    def get_average_rate(self, property):
        return property.reviews.all().aggregate(Avg('rate'))

    # location_geo = serializers.SerializerMethodField(method_name='get_user_location')
    #
    # def get_user_location(self, property):
    #     geo = GeoIP2()
    #     ip = self.context.get('request').META.get('REMOTE_ADDR')
    #     return geo.geos('94.122.149.41').wkt


class ReservationSerializer(serializers.ModelSerializer):
    """
    Create base reservation serializer for http methods except for post and patch
    """

    guest = serializers.HiddenField(default=serializers.CurrentUserDefault())
    property = PropertySerializer
    available_from = serializers.DateTimeField(source='property.available_to', read_only=True)
    available_to = serializers.DateTimeField(source='property.available_to', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'guest', 'property', 'reservation_from', 'reservation_to', 'reserved',
                  'reservation_in_nights', 'reservation_fees', 'total_fees', 'available_from',
                  'available_to']
        read_only_fields = ['available_from', 'available_to']

    # Custom field for reservation duration in days
    reservation_in_nights = serializers.SerializerMethodField(method_name='get_reservation_in_nights')

    # Custom field for reservation fee calculation
    reservation_fees = serializers.SerializerMethodField(method_name='calculate_reservation_fees')

    # Custom field for total fees
    total_fees = serializers.SerializerMethodField(method_name='calculate_total_fees')

    def get_reservation_in_nights(self, reservation):
        start_date = reservation.reservation_from
        end_date = reservation.reservation_to
        return abs((end_date - start_date).days)

    def calculate_reservation_fees(self, reservation):
        reservation_fees = reservation.property.price_per_night * self.get_reservation_in_nights(reservation)
        return reservation_fees

    def calculate_total_fees(self, reservation):
        """
        Assumption: total reservations fees are service fees in 12% added to reservation fees
        :param reservation:
        :return:
        """
        service_fees = (Decimal(0.12) * self.calculate_reservation_fees(reservation))
        return service_fees + self.calculate_reservation_fees(reservation)


class CreateReservationSerializer(serializers.ModelSerializer):
    """
    Create custom serializer for http method post (reservation creation action)
    """
    guest = serializers.HiddenField(default=serializers.CurrentUserDefault())
    reserved = serializers.HiddenField(default=False)
    # available_from = serializers.DateTimeField(source='property.available_to', read_only=True)
    # available_to = serializers.DateTimeField(source='property.available_to', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'guest', 'property', 'reservation_from', 'reservation_to', 'reserved']

    def validate(self, attrs):
        """
        Custom validation for reservation fields on create
        :param attrs:
        :return:
        """
        # custom reservation property validation
        property_instance = attrs['property']
        if Property.objects.filter(id=property_instance.id, available=False).exists():
            raise serializers.ValidationError('Property does not exist')

        if Reservation.objects.filter(property_id=property_instance.id, reserved=True).exists():
            raise serializers.ValidationError('This property is currently reserved')

        # Custom reservation dates validation
        if attrs['reservation_from'] > attrs['reservation_to']:
            raise serializers.ValidationError('Reservation must occur in available dates')

        if attrs['reservation_from'] < property_instance.available_from:
            raise serializers.ValidationError('Reservation from date must occur when the property is available')

        if attrs['reservation_to'] > property_instance.available_to:
            raise serializers.ValidationError('Reservation to date must occur when the property is available')

        # Custom user type validation
        user = self.context['request'].user
        if user.role != 'guest':
            raise serializers.ValidationError('Reservation is available only for guest user type')

        return attrs


class UpdateReservationSerializer(serializers.ModelSerializer):
    """
    Create custom serializer for http method patch (reservation update action)
    """

    class Meta:
        model = Reservation
        fields = ['reservation_from', 'reservation_to']
