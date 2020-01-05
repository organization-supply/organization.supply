from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from api.serializers import (
    InventorySerializer,
    LocationSerializer,
    MutationSerializer,
    ProductSerializer,
    NotificationSerializer,
)
from organization.models import Inventory, Location, Mutation, Organization, Product
from notifications import Notification

def save_serializer_with_organization(serializer, organization):
    if serializer.instance:  # We are updating
        status = HTTP_200_OK
    else:
        status = HTTP_201_CREATED

    if serializer.is_valid():
        # Assign the organization
        serializer.validated_data["organization"] = get_object_or_404(
            Organization, slug=organization
        )
        serializer.save()
        return Response(serializer.data, status=status)
    else:
        return Response(
            {
                "message": "An error occured with the operation",
                "errors": serializer.errors,
            },
            status=HTTP_400_BAD_REQUEST,
        )


class ApiAuthorize(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "organization": request.organization.slug,
                "user": user.username,
            }
        )


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing notifications.
    """
    serializer_class = NotificationSerializer

    def list(self, request, organization):
        queryset = Notification.objects.filter(recipient=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductView(generics.ListCreateAPIView):

    serializer_class = ProductSerializer

    def list(self, request, organization):
        """
        A list of all the products within the organization
        """
        queryset = Product.objects.for_organization(organization)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, organization):
        """
        Create a product within the organization
        """
        serializer = self.get_serializer(data=request.data)
        return save_serializer_with_organization(serializer, organization)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = ProductSerializer

    def get(self, request, pk, organization):
        """
        Get a single product by ID
        """
        queryset = Product.objects.for_organization(organization)
        product = get_object_or_404(Product, pk=pk)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    def put(self, request, pk, organization):
        """
        Update a single product by ID
        """
        queryset = Product.objects.for_organization(organization)
        product = get_object_or_404(Product, pk=pk)
        serializer = self.get_serializer(product, data=request.data)
        return save_serializer_with_organization(serializer, organization)

    def patch(self, request, pk, organization):
        """
        Update a single product by ID

        """
        queryset = Product.objects.for_organization(organization)
        product = get_object_or_404(Product, pk=pk)
        serializer = self.get_serializer(product, data=request.data)
        return save_serializer_with_organization(serializer, organization)

    def delete(self, request, pk, organization):
        """
        Delete a single product by ID
        """
        queryset = Product.objects.for_organization(organization)
        product = get_object_or_404(queryset, pk=pk)
        product.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class LocationView(generics.ListCreateAPIView):

    serializer_class = LocationSerializer

    def list(self, request, organization):
        queryset = Location.objects.for_organization(organization)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, organization):
        serializer = LocationSerializer(data=request.data)
        return save_serializer_with_organization(serializer, organization)


class LocationDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = LocationSerializer

    def get(self, request, pk, organization):
        """
        Get a single product by ID
        """
        queryset = Location.objects.for_organization(organization)
        location = get_object_or_404(Location, pk=pk)
        serializer = self.get_serializer(location)
        return Response(serializer.data)

    def put(self, request, pk, organization):
        """
        Update a single location by ID
        """
        queryset = Location.objects.for_organization(organization)
        location = get_object_or_404(Location, pk=pk)
        serializer = self.get_serializer(location, data=request.data)
        return save_serializer_with_organization(serializer, organization)

    def patch(self, request, pk, organization):
        """
        Update a single location by ID
        """
        queryset = Location.objects.for_organization(organization)
        location = get_object_or_404(Location, pk=pk)
        serializer = self.get_serializer(location, data=request.data)
        return save_serializer_with_organization(serializer, organization)

    def delete(self, request, pk, organization):
        """
        Delete a single location by ID
        """
        queryset = Location.objects.for_organization(organization)
        location = get_object_or_404(queryset, pk=pk)
        location.delete()
        return Response(status=HTTP_204_NO_CONTENT)


# # class InventoryViewSet(viewsets.ViewSet):
# #     """
# #     list:
# #     A list of the inventory of the organization

# #     retrieve:
# #     Get a detailed overview of a single inventory (location and product specific)
# #     """

# #     def list(self, request, organization):
# #         queryset = Inventory.objects.for_organization(organization)
# #         serializer = InventorySerializer(queryset, many=True)
# #         return Response(serializer.data)

# #     def retrieve(self, request, organization, pk=None):
# #         queryset = Inventory.objects.for_organization(organization)
# #         inventory = get_object_or_404(queryset, pk=pk)
# #         serializer = InventorySerializer(inventory)
# #         return Response(serializer.data)


# # class MutationViewSet(viewsets.ViewSet):
# #     """
# #     list:
# #     All the mutations of the organization

# #     retrieve:
# #     Get a single mutation and its details
# #     """

# #     def list(self, request, organization):
# #         queryset = Mutation.objects.for_organization(organization)
# #         serializer = MutationSerializer(queryset, many=True)
# #         return Response(serializer.data)

# #     def retrieve(self, request, organization, pk=None):
# #         queryset = Mutation.objects.for_organization(organization)
# #         mutation = get_object_or_404(queryset, pk=pk)
# #         serializer = MutationSerializer(mutation)
# #         return Response(serializer.data)
