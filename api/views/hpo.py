from rest_framework import viewsets
from home.models import HPO
from api.serializers import HPOSerializer


class HPOViewSet(viewsets.ModelViewSet):
    serializer_class = HPOSerializer
    queryset = HPO.objects.all()
    http_method_names = ['get', 'head', 'options']
