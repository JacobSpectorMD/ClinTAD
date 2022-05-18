from rest_framework import viewsets
from home.models import Element
from api.serializers import ElementSerializer


class ElementViewSet(viewsets.ModelViewSet):
    serializer_class = ElementSerializer
    queryset = Element.objects.all()
    http_method_names = ['get', 'head', 'options']
