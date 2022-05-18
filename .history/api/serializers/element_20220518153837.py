from rest_framework import serializers
from home.models import Element 
mport ChromosomeSerializer​


class ElementSerializer(serializers.HyperlinkedModelModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    track = TrackSerializer(many=False, read_only=True)
    class Meta:
        model = Element 
        fields = ['id', 'track', 'chromosome']

