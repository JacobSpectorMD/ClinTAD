from rest_framework import serializers
from home.models import Build


class BuildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Build
        fields = ['id', 'long_name', 'name']


