from rest_framework import serializers

from api.serializers import BuildSerializer
from api.serializers.simple import SimpleChromosomeSerializer, SimpleTrackSerializer
from home.models import Element


class ElementSerializer(serializers.ModelSerializer):
    build = BuildSerializer(many=False, read_only=True)
    chromosome = SimpleChromosomeSerializer(many=False, read_only=True)
    track = SimpleTrackSerializer(many=False, read_only=True)

    class Meta:
        model = Element 
        fields = '__all__'