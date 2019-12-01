from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from api.serializers import InventorySerializer, LocationSerializer, ProductSerializer
from organization.models import Inventory, Location, Product


class ApiAuthorize(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'organization': request.organization.slug,
            'user': user.pk,
        })


class ProductViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Product.objects.for_organization(request.organization)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Product.objects.for_organization(request.organization)
        user = get_object_or_404(queryset, pk=pk)
        serializer = ProductSerializer(user)
        return Response(serializer.data)


class LocationViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Location.objects.for_organization(request.organization)
        serializer = LocationSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Location.objects.for_organization(request.organization)
        user = get_object_or_404(queryset, pk=pk)
        serializer = LocationSerializer(user)
        return Response(serializer.data)


class InventoryViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Inventory.objects.for_organization(request.organization)
        serializer = InventorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Inventory.objects.for_organization(request.organization)
        user = get_object_or_404(queryset, pk=pk)
        serializer = InventorySerializer(user)
        return Response(serializer.data)
