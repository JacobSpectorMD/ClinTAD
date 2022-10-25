from rest_framework import serializers
from home.models import HPO


class HPOSerializer(serializers.ModelSerializer):
    class Meta:
        model = HPO
        fields = '__all__'
