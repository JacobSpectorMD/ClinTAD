from rest_framework import serializers

from api.serializers import BuildSerializer
from home.models import Chromosome


class ChromosomeSerializer(serializers.ModelSerializer):
    build = BuildSerializer(many=False, read_only=True)
    """
    Chromosome serializer
    """
    class Meta:
        model = Chromosome
        fields = '__all__'
