from rest_framework import serializers

from bunnies.models import RabbitHole


class NearbyRabbitHoleSerializer(serializers.Serializer):
    """
    Serializes the name, distance and general direction of a rabbit hole with respect
    to the current position of a given fox.
    """
    location = serializers.CharField()
    distance_km = serializers.FloatField()
    compass_direction = serializers.ChoiceField(choices=["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

    class Meta:
        model = RabbitHole
