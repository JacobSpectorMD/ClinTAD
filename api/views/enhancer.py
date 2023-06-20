from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from django.db.models import Q

from api.serializers import EnhancerSerializer
from home.models import Enhancer


# Needs track info
class EnhancerViewSet(viewsets.ModelViewSet):
    """
        The default VISTA enhancer track contains Enhancer objects.
    """
    serializer_class = EnhancerSerializer
    queryset = Enhancer.objects.all()
    http_method_names = ['get', 'head', 'options']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='chromosome_number', description='The number of the chromosome the enhancer is on '
                                                                   '(1 - 22, X, Y).',
                             required=False, type=str),
            OpenApiParameter(name='coordinates', description='Find enhancers that overlap certain coordinates. '
                                                             'Should be in the format of start-end, e.g. '
                                                             '1,250,000-2,800,000.',
                             required=False, type=str),
            OpenApiParameter(name='build_name', description='The name of the build the element belongs to, e.g. hg19.',
                             required=False, type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request)

    def get_queryset(self):
        queryset = Enhancer.objects.all()
        chromosome = self.request.query_params.get('chromosome_number')
        coordinates = self.request.query_params.get('coordinates')
        build = self.request.query_params.get('build_name')
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
