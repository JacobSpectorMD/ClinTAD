from rest_framework import serializers
from home.models import Variant


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = '__all__'
