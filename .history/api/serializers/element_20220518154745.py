from rest_framework import serializers
from home.models import Element 
from api.serializers.chromosome import ChromosomeSerializer
from api.serializers.track import TrackSerializer


class ElementSerializer(serializers.HyperlinkedModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    track = TrackSerializer(many=False, read_only=True)
    class Meta:
        model = Element 
        fields = ['id', 'track', 'chromosome']

    def create(self, validated_data) :
        chromosome = validated_data.pop('chromosome', [])
        element = super().create(validated_data)
        chr_qs = chromosome.objects.filter(name__in=chromosome)
        

