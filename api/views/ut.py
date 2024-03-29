from rest_framework import viewsets
from home.models import UT
from api.serializers import UTSerializer

#NO -- probably needs authentication first
class UTViewSet(viewsets.ModelViewSet):
    serializer_class = UTSerializer
    queryset = UT.objects.all()
    http_method_names = ['get', 'head', 'options']
