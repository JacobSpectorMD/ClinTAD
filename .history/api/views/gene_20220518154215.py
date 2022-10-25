from rest_framework import viewsets
from home.models import Gene
from api.serializers import GeneSerializer


class GeneViewSet(viewsets.ModelViewSet):
    serializer_class = GeneSerializer
    

    def get_queryset(self):
        name = self.request.GET.get('name', None)
        if name == None:
            return Gene.objects.first()
        else:
            return Gene.objects.filter(name=name)

http_method_names = ['get', 'head', 'options']