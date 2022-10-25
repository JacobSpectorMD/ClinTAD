from rest_framework import serializers
from home.models import TAD


class TADSerializer(serializers.ModelSerializer):
    class Meta:
        model = TAD
        fields = '__all__'
