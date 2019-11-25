from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from organization.models import Product, Location, Inventory
from api.serializers import ProductSerializer, LocationSerializer, InventorySerializer

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