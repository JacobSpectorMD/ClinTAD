from rest_framework import serializers
from home.models import Element 
from api.serializers import ChromosomeSerializer​


class ElementSerializer(serializers.HyperlinkedModelModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    track = TrackSerializer(many=False, read_only=True)
    class Meta:
        model = Element 
        fields = ['id']


class GeneSerializer(serializers.HyperlinkedModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    class Meta:
        model = Message
        fields = ['chromosome', 'name', 'id']    
