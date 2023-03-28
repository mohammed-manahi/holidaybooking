from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """
    Customize base user manager class
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save regular user with a given email and password
        :param email:
        :param password:
        :param extra_fields:
        :return:
        """
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with a given email and password
        :param email:
        :param password:
        :param extra_fields:
        :return:
        """
        email = self.normalize_email(email)
        superuser = self.model(email=email, username=email, **extra_fields)
        superuser.set_password(password)
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save(using=self._db)
        return superuser


class User(AbstractUser, PermissionsMixin):
    """
    Customize default django authentication user model by inheriting abstract user
    """
    HOST = 'host'
    GUEST = 'guest'

    USER_ROLE = [
        (HOST, HOST),
        (GUEST, GUEST),
    ]

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    role = models.CharField(max_length=10, choices=USER_ROLE, default=GUEST)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/', blank=True)

    objects = UserManager()

    # Set username field to email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role', 'date_of_birth', 'photo']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name

    def get_role(self):
        return self.role

    def __str__(self):
        return self.get_full_name()
