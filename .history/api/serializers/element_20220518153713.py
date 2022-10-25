from rest_framework import serializers
from home.models import Element 
from api.serializers import ChromosomeSerializer​


class ElementSerializer(serializers.HyperlinkedModelModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    class Meta:
        model = Element 
        fields = '__all__' 


class GeneSerializer(serializers.HyperlinkedModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    class Meta:
        model = Message
        fields = ['chromosome', 'name', 'id']    
