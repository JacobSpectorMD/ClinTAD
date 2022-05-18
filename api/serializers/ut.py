from rest_framework import serializers
from home.models import UT


class UTSerializer(serializers.ModelSerializer):
    class Meta:
        model = UT
        fields = '__all__'
