from rest_framework import serializers
from api.serializers import ChromosomeSerializer
from home.models import Gene, HPO, Omim


class GeneHpoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HPO
        fields = ['']


class GeneOmimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Omim
        fields = ['id', 'omim_number', 'title']


class GeneSerializer(serializers.ModelSerializer):
    chromosome = ChromosomeSerializer(many=False, read_only=True)
    omims = GeneOmimSerializer(many=True, read_only=True)

    class Meta:
        model = Gene
        fields = '__all__'
