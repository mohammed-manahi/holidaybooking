import stripe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from reservation.models import Property, Category, Media, Feature, FeatureCategory, Review, Reservation
from reservation.serializers import PropertySerializer, CategorySerializer, MediaSerializer, ReviewSerializer, \
    FeatureCategorySerializer, FeatureSerializer, ReservationSerializer, CreateReservationSerializer, \
    UpdateReservationSerializer
from reservation.permissions import CanAddOrUpdateProperty, AdminOnlyActions
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view


class PropertyViewSet(ModelViewSet):
    """
    Create view set for property model
    """
    # Use django-filter library to apply generic back-end filtering and search filter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Add search filter fields
    search_fields = ['name', 'description']

    # Add sorting filter fields
    ordering_fields = ['name', 'price_per_night']

    # Set custom permission class
    permission_classes = [IsAuthenticated, CanAddOrUpdateProperty]

    def get_queryset(self):
        """
        Define property api query-set
        :return:
        """
        return Property.objects.select_related('category').prefetch_related('media').all()

    def get_serializer_class(self):
        """
        Define property api serializer
        :return:
        """
        return PropertySerializer

    def get_serializer_context(self):
        """
        Define property api context
        :return:
        """
        return {'request': self.request}


class CategoryViewSet(ModelViewSet):
    """
    Create view set for category model
    """
    # Use django-filter library to apply generic back-end filtering and search filter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Add search filter fields
    search_fields = ['name', 'description']

    # Add sorting filter fields
    ordering_fields = ['name']

    # Set permission classes
    permission_classes = [IsAuthenticated, AdminOnlyActions]

    def get_queryset(self):
        """
        Define category api query-set
        :return:
        """
        return Category.objects.prefetch_related('properties').all()

    def get_serializer_class(self):
        """
        Define category api serializer
        :return:
        """
        return CategorySerializer

    def get_serializer_context(self):
        """
        Define property api context
        :return:
        """
        return {'request': self.request}


class MediaViewSet(ModelViewSet):
    """
    Create media view set for media model
    """
    # Set  permission classes
    permission_classes = [IsAuthenticated, CanAddOrUpdateProperty]

    def get_queryset(self):
        """
        Define media api queryset
        :return:
        """
        return Media.objects.filter(property_id=self.kwargs.get('property_pk'))

    def get_serializer_class(self):
        """
         Define media api serializer
        :return:
        """
        return MediaSerializer

    def get_serializer_context(self):
        """
        Define media api context
        :return:
        """
        return {'request': self.request, 'property_id': self.kwargs.get('property_pk')}


class ReviewViewSet(ModelViewSet):
    """
    Create review view set for review model
    """
    # Set permission classes
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Define review api queryset
        :return:
        """
        return Review.objects.filter(property_id=self.kwargs.get('property_pk'))

    def get_serializer_class(self):
        """
        Define review api serializer
        :return:
        """
        return ReviewSerializer

    def get_serializer_context(self):
        """
        Define review api context
        :return:
        """
        return {'request': self.request, 'property_id': self.kwargs.get('property_pk')}


class FeatureCategoryViewSet(ModelViewSet):
    """
    Create feature category view set for feature category model
    """
    # Set permission classes
    permission_classes = [IsAuthenticated, AdminOnlyActions]

    def get_queryset(self):
        """
        Define feature category api queryset
        :return:
        """
        return FeatureCategory.objects.all()

    def get_serializer_class(self):
        """
        Define feature category api serializer
        :return:
        """
        return FeatureCategorySerializer

    def get_serializer_context(self):
        """
        Define feature category api context
        :return:
        """
        return {'request': self.request}


class FeatureViewSet(ModelViewSet):
    """
    Create feature view set for feature model
    """
    # Set permission classes
    permission_classes = [IsAuthenticated, CanAddOrUpdateProperty]

    def get_queryset(self):
        """
        Define feature api queryset
        :return:
        """
        return Feature.objects.select_related('property').filter(property_id=self.kwargs.get('property_pk'))

    def get_serializer_class(self):
        """
        Define feature api serializer
        :return:
        """
        return FeatureSerializer

    def get_serializer_context(self):
        """
        Define feature api context
        :return:
        """
        return {'request': self.request, 'property_id': self.kwargs.get('property_pk')}


class ReservationViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, GenericViewSet):
    """
    Create reservation view set
    """
    # Define allowed http methods
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    # Set permission classes
    permission_classes = [IsAuthenticated]

    # Use django-filter library to apply generic back-end filtering and search filter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Add search filter fields
    search_fields = ['reservation_from', 'reservation_to']

    def get_queryset(self):
        """
        Define reservation API query-set
        :return:
        """
        return Reservation.objects.all()

    def get_serializer_class(self):
        """
        Define reservation api serializer
        :return:
        """
        # Define order API serializer based on http method
        if self.request.method == 'POST':
            return CreateReservationSerializer
        if self.request.method == 'PATCH':
            return UpdateReservationSerializer
        return ReservationSerializer

    def get_serializer_context(self):
        """
        Define reservation api context
        :return:
        """
        return {'request': self.request}

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Process payment
        process_payment(request)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def process_payment(request):
    reservation_id = request.data.get('reservation_id')
    reservation = Reservation.objects.get(id=reservation_id)

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        # Create a Stripe charge
        charge = stripe.Charge.create(
            amount=int(reservation.total_fees * 100),
            currency='usd',
            description='Reservation payment',
            source=request.data['stripeToken']
        )

        # Update reservation status
        reservation.save()

        # Return a success response
        return JsonResponse({'success': True})

    except stripe.error.CardError as e:
        # Return an error response if the charge fails
        return JsonResponse({'error': str(e)})
