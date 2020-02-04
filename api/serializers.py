from rest_framework import serializers

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.notifications import Notification


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "desc"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "desc"]


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["id", "product", "location", "amount"]


class MutationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mutation
        fields = ["id", "amount", "product", "location", "desc", "operation"]


class NotificationSerializer(serializers.Serializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "timestamp",
            "description",
            "verb",
            "actor_object_content_type",
            "actor_object_id",
            "action_object_content_type",
            "action_object_id",
        ]
