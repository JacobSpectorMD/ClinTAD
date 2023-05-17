from rest_framework import serializers

from home.models import Track


class SimpleTrackSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(source='creator.name')

    class Meta:
        model = Track
        fields = ['id', 'label', 'creator']
