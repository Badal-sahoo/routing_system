from rest_framework import serializers


class AgentLocationSerializer(serializers.Serializer):
    """Validates a single GPS ping. Coordinate precision matches the Node model."""

    lat = serializers.DecimalField(
        max_digits=11, decimal_places=8, min_value=-90, max_value=90
    )
    lng = serializers.DecimalField(
        max_digits=11, decimal_places=8, min_value=-180, max_value=180
    )
