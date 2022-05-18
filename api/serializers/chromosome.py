from rest_framework import serializers
from home.models import Chromosome


class ChromosomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chromosome
        fields = '__all__'
