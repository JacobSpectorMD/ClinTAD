from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework import status, viewsets

from home.models import Chromosome
from api.serializers import ChromosomeSerializer


class ChromosomeViewSet(viewsets.ModelViewSet):
    """
        This model has data about chromosome length and is used to track which chromosome CNVs are on.
    """
    serializer_class = ChromosomeSerializer
    queryset = Chromosome.objects.all()
    http_method_names = ['get', 'head', 'options']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='build_name', description='The name of the build associated with the '
                                                            'chromosome, e.g. hg19.', required=False, type=str),
            OpenApiParameter(name='number', description='The chromosome number (1 - 22, X, Y)', required=False,
                             type=str),
        ]
    )
    def list(self, request):
        return super().list(request)

    def get_queryset(self):
        queryset = Chromosome.objects.all()
        number = self.request.query_params.get('number')
        build = self.request.query_params.get('build_name')
        if number:
            queryset = queryset.filter(number__iexact=number)
        if build:
            queryset = queryset.filter(build__long_name__icontains=build)
        return queryset