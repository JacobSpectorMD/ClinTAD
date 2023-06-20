from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from django.db.models import Q

from api.serializers import GeneSerializer
from home.models import Gene


class GeneViewSet(viewsets.ModelViewSet):
    serializer_class = GeneSerializer
    http_method_names = ['get', 'head', 'options']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='build_name', description='The name of the build the gene belongs to, e.g. hg19.',
                             required=False, type=str),
            OpenApiParameter(name='chromosome_number', description='The number of the chromosome the gene is on '
                                                                   '(1 - 22, X, Y).', required=False, type=str),
            OpenApiParameter(name='coordinates', description='Find genes that overlap certain coordinates. '
                                                             'Should be in the format of start-end, e.g. '
                                                             '1,250,000-2,800,000.', required=False, type=str),
            OpenApiParameter(name='name', description='The name of the gene.', required=False, type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request)

    def get_queryset(self):
        queryset = Gene.objects.all()
        build = self.request.query_params.get('build_name')
        chromosome = self.request.query_params.get('chromosome_number')
        coordinates = self.request.query_params.get('coordinates')
        name = self.request.query_params.get('name')
        if chromosome:
            queryset = queryset.filter(chromosome__number__iexact=chromosome)
        if coordinates:
            start = int(coordinates.split('-')[0].replace(',', ''))
            end = int(coordinates.split('-')[1].replace(',', ''))
            queryset = queryset.filter(
                Q(start__range=(start, end)) |  # The start of the enhancer is within the coordinates
                Q(end__range=(start, end)) |  # The end of the enhancer is within the coordinates
                Q(start__lte=start, end__gte=end)  # The enhancer completely contains the coordinates
            )
        if build:
            queryset = queryset.filter(build__long_name__icontains=build)
        return queryset
