from rest_framework import serializers
from reservation.models import Property


class PropertySerializer(serializers.ModelSerializer):
    """
    Create serializer for property model
    """
    # Get current authenticated user
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        """
        Custom validation for available from and available to fields
        :param attrs:
        :return:
        """
        if attrs['available_from'] > attrs['available_to']:
            raise serializers.ValidationError('Available to date must occur after available from date')
        return attrs

    class Meta():
        model = Property
        fields = ['id', 'name', 'description', 'slug', 'owner', 'address', 'size', 'location', 'number_of_bedrooms',
                  'number_of_beds', 'number_of_baths', 'number_of_adult_guests', 'number_of_child_guests',
                  'price_per_night', 'deposit', 'available', 'available_from', 'available_to', 'cancellation_policy',
                  'cancellation_fee_per_night']
