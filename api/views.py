from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from api.serializers import (
    InventorySerializer,
    LocationCreateSerializer,
    LocationSerializer,
    MutationSerializer,
    ProductCreateSerializer,
    ProductSerializer,
)
from organization.models import Inventory, Location, Mutation, Product


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


class ProductViewSet(viewsets.ViewSet):
    """
    list:
    A list of all the products in the organization

    retrieve:
    Get a single product and its details

    create:
    Create a new product within the organization

    destroy:
    Delete a product (only possible if there is no inventory)
    """

    def list(self, request):
        queryset = Product.objects.for_organization(request.organization)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Product.objects.for_organization(request.organization)
        product = get_object_or_404(queryset, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def create(self, request):
        request.data.update(organization=request.organization)
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=HTTP_201_CREATED)
        else:
            return Response(
                {"message": "Product could not be created with received data."},
                status=HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk=None):
        queryset = Product.objects.for_organization(request.organization)
        product = get_object_or_404(queryset, pk=pk)
        product.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class LocationViewSet(viewsets.ViewSet):
    """
    list:
    A list of all the locations in the organization

    retrieve:
    Get a single location and its details

    create:
    Create a new location within the organization

    destroy:
    Delete a location (only possible if there is no inventory)
    """

    def list(self, request, organization):
        queryset = Location.objects.for_organization(organization)
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, organization, pk=None):
        queryset = Location.objects.for_organization(organization)
        location = get_object_or_404(queryset, pk=pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data)

    def create(self, request):
        request.data.update(organization=request.organization)
        serializer = LocationCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=HTTP_201_CREATED)
        else:
            return Response(
                {"message": "Product could not be created with received data."},
                status=HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, pk=None):
        queryset = Location.objects.for_organization(request.organization)
        location = get_object_or_404(queryset, pk=pk)
        location.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class InventoryViewSet(viewsets.ViewSet):
    """
    list:
    A list of the inventory of the organization

    retrieve:
    Get a detailed overview of a single inventory (location and product specific)
    """

    def list(self, request, organization):
        queryset = Inventory.objects.for_organization(organization)
        serializer = InventorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, organization, pk=None):
        queryset = Inventory.objects.for_organization(organization)
        inventory = get_object_or_404(queryset, pk=pk)
        serializer = InventorySerializer(inventory)
        return Response(serializer.data)


class MutationViewSet(viewsets.ViewSet):
    """
    list:
    All the mutations of the organization

    retrieve:
    Get a single mutation and its details
    """

    def list(self, request, organization):
        queryset = Mutation.objects.for_organization(organization)
        serializer = MutationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, organization, pk=None):
        queryset = Mutation.objects.for_organization(organization)
        mutation = get_object_or_404(queryset, pk=pk)
        serializer = MutationSerializer(mutation)
        return Response(serializer.data)
