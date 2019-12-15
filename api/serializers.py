from rest_framework import serializers

from organization.models import Inventory, Location, Mutation, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "desc"]


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "desc", "organization"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "desc"]


class LocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "desc", "organization"]


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["id", "product", "location", "amount"]


class MutationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mutation
        fields = ["id", "amount", "product", "location", "desc", "operation"]
