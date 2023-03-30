from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from reservation.models import Property
from reservation.serializers import PropertySerializer


#
# class PropertyList(APIView):
#     """ Class-based view for property list using APIView class """
#
#     def get(self, request):
#         properties = Property.objects.all()
#         serializer = PropertySerializer(properties, many=True, context={'request': request})
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = PropertySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class PropertyDetail(APIView):
#     """ Class-based view for property detail using APIView class """
#
#     def get(self, request, pk):
#         property = get_object_or_404(Property, pk=pk)
#         serializer = PropertySerializer(property)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         property = get_object_or_404(Property, pk=pk)
#         serializer = PropertySerializer(instance=property, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         property = get_object_or_404(Property, pk=pk)
#         property.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
class PropertyViewSet(ModelViewSet):
    """
    Create view set for property model
    """
    # Set custom permission class
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Define property api query-set
        :return:
        """
        return Property.objects.all()

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
