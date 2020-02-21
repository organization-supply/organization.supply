from rest_framework import serializers

from organization.models.inventory import Inventory, Location, Mutation, Product
from organization.models.notifications import Notification
from user.models import User


class TagSerializerField(serializers.ListField):
    child = serializers.CharField()

    def to_representation(self, data):
        return data.values_list('name', flat=True)


# class TagSerializer(serializers.ModelSerializer):
#     tags = TagSerializerField()

#     def create(self, validated_data):
#         tags = validated_data.pop('tags')
#         instance = super(TagSerializer, self).create(validated_data)
#         instance.tags.set(*tags)
#         return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name"]

class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializerField(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "desc", "price_cost", "price_sale", "tags"]


class LocationSerializer(serializers.ModelSerializer):
    tags = TagSerializerField(read_only=True)

    class Meta:
        model = Location
        fields = ["id", "name", "desc", "size", "tags"]


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ["id", "product", "location", "amount"]


class MutationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mutation
        fields = ["id", "amount", "product", "location", "desc", "operation"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "timestamp",
            "description",
            "verb",
        ]