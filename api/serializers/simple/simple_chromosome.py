from rest_framework import serializers

from home.models import Chromosome


class SimpleChromosomeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chromosome
        fields = ['id', 'number']
