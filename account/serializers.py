from django.contrib.auth import get_user_model
from djoser import serializers

# Use get user model method which is a lookup method for AUTH_USER_MODEL in settings
User = get_user_model()


class UserCreateSerializer(serializers.UserCreateSerializer):
    """
    Extend user create serializer in djoser to create new user
    """

    class Meta(serializers.UserCreateSerializer.Meta):
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'role', 'date_of_birth', 'photo']
