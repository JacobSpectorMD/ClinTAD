from rest_framework import serializers
from home.models import Element 
from api.serializers.chromosome import ChromosomeSerializer
from api.serializers.track import TrackSerializer


class ElementSerializer(serializers.HyperlinkedModelSerializer):
    chromosome = ChromosomeSerializerStringRelatedField(many=False, read_only=True)
    track = TrackSerializer(many=False, read_only=True)
    class Meta:
        model = Element 
        fields = ['id', 'track', 'chromosome']

