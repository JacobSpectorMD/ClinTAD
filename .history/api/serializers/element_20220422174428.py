from rest_framework import serializers
from home.models import Element 


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element 
        fields = '__all__' 
