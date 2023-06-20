from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from api.paginators import SmallPaginator
from api.serializers import ElementSerializer
from home.models import Element


class ElementViewSet(viewsets.ModelViewSet):
    """
        Custom user tracks have Elements that represent TADs, CNVs, etc.
    """
    serializer_class = ElementSerializer
    pagination_class = SmallPaginator
    queryset = Element.objects.all().order_by('id')
    http_method_names = ['get', 'head', 'options']

    @extend_schema(
        parameters=[
            OpenApiParameter(name='track_id', description='The ID number of the track the element belongs to',
                             required=False, type=int),
            OpenApiParameter(name='build_name', description='The name of the build the element belongs to, e.g. hg19.',
                             required=False, type=str),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request)

    def get_queryset(self):
        # Only allow users to see elements that are in public tracks, or that are from their own tracks
        public_queryset = Element.objects.filter(track__public=True)
        track_id = self.request.query_params.get('track_id')
        build = self.request.query_params.get('build_name')
        if track_id:
            public_queryset = public_queryset.filter(track_id=track_id)
        if build:
            public_queryset = public_queryset.filter(build__long_name__icontains=build)

        user_queryset = Element.objects.filter(track__creator=self.request.user)
        if track_id:
            user_queryset = user_queryset.filter(track_id=track_id)
        if build:
            user_queryset = user_queryset.filter(build__long_name__icontains=build)

        queryset = (public_queryset | user_queryset).distinct()
        return queryset
