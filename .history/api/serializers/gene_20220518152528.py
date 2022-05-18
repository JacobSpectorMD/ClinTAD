from rest_framework import serializers
from api.serializers import ChromosomeSerializer
from home.models import Gene

class GeneSerializer(serializers.ModelSerializer):
    chromosome = ChromosomeSerializer.PrimaryKeyRelatedField(many=False, read_only=True)
    class Meta:
        model = Gene
        fields = ['chromosome', 'name', 'id']    
