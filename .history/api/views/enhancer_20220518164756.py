from rest_framework import viewsets
from home.models import Enhancer
from api.serializers import EnhancerSerializer

# Needs track info
class EnhancerViewSet(viewsets.ModelViewSet):
    serializer_class = EnhancerSerializer
    queryset = Enhancer.objects.all()
    http_method_names = ['get', 'head', 'options']
