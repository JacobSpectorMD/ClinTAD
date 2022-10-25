from rest_framework import viewsets
from home.models import Chromosome
from api.serializers import ChromosomeSerializer


class ChromosomeViewSet(viewsets.ModelViewSet):
    serializer_class = ChromosomeSerializer
    queryset = Chromosome.objects.all()
    http_method_names = ['get', 'head', 'options']
