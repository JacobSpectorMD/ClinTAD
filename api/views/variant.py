from rest_framework import viewsets
from home.models import Variant
from api.serializers import VariantSerializer


class VariantViewSet(viewsets.ModelViewSet):
    serializer_class = VariantSerializer
    queryset = Variant.objects.all()
    http_method_names = ['get', 'head', 'options']
