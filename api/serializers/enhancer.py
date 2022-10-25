from rest_framework import serializers
from home.models import Enhancer


class EnhancerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enhancer
        fields = '__all__'
