from rest_framework import serializers

from home.models import Enhancer


class EnhancerSerializer(serializers.ModelSerializer):
    build_long_name = serializers.CharField(source='build.long_name')
    chromosome_number = serializers.CharField(source='chromosome.number')

    class Meta:
        model = Enhancer
        fields = '__all__'