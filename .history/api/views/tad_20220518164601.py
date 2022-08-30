from rest_framework import viewsets
from home.models import TAD
from api.serializers import TADSerializer

#NO
class TADViewSet(viewsets.ModelViewSet):
    serializer_class = TADSerializer
    queryset = TAD.objects.all()
    http_method_names = ['get', 'head', 'options']
