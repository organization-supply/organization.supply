from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from api.serializers import (
    InventorySerializer,
    LocationSerializer,
    MutationSerializer,
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
    def list(self, request, organization):
        queryset = Product.objects.for_organization(organization)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, organization, pk=None):
        queryset = Product.objects.for_organization(organization)
        user = get_object_or_404(queryset, pk=pk)
        serializer = ProductSerializer(user)
        return Response(serializer.data)


class LocationViewSet(viewsets.ViewSet):
    def list(self, request, organization):
        queryset = Location.objects.for_organization(organization)
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, organization, pk=None):
        queryset = Location.objects.for_organization(organization)
        user = get_object_or_404(queryset, pk=pk)
        serializer = LocationSerializer(user)
        return Response(serializer.data)


class InventoryViewSet(viewsets.ViewSet):
    def list(self, request, organization):
        queryset = Inventory.objects.for_organization(organization)
        serializer = InventorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, organization, pk=None):
        queryset = Inventory.objects.for_organization(organization)
        user = get_object_or_404(queryset, pk=pk)
        serializer = InventorySerializer(user)
        return Response(serializer.data)


class MutationViewSet(viewsets.ViewSet):
    def list(self, request, organization):
        queryset = Mutation.objects.for_organization(organization)
        serializer = MutationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, organization, pk=None):
        queryset = Mutation.objects.for_organization(organization)
        user = get_object_or_404(queryset, pk=pk)
        serializer = MutationSerializer(user)
        return Response(serializer.data)
