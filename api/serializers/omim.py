from rest_framework import serializers
from home.models import Omim


class OmimSerializer(serializers.ModelSerializer):

    class Meta:
        model = Omim
        fields = '__all__'
