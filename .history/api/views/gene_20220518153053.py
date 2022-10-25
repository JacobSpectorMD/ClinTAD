from rest_framework import viewsets
from home.models import Gene
from api.serializers import GeneSerializer


class GeneViewSet(viewsets.ModelViewSet):
    serializer_class = GeneSerializer
    http_method_names = ['get', 'head', 'options']
    queryset = Gene.objects.all()

    def get_queryset(queryset):
        name = self.request.GET.get('name', None)
        if name is None:
            return Gene.objects.first()
        else:
            return Gene.objects.filter(name=name)
