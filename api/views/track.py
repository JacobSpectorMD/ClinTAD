from rest_framework import viewsets
from home.models import Track
from api.serializers import TrackSerializer


class TrackViewSet(viewsets.ModelViewSet):
    serializer_class = TrackSerializer
    queryset = Track.objects.all()
    http_method_names = ['get', 'head', 'options']
