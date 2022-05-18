from rest_framework import serializers
from home.models import Element 


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element 
        fields = '__all__' 

from rest_framework import serializers
from api.serializers import ChromosomeSerializer​
class GeneSerializer(serializers.HyperlinkedModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    class Meta:
        model = Message
        fields = ['chromosome', 'name', 'id']    
