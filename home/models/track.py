from django.db import models
from django.db.models import Q


class Track(models.Model):
    build = models.ForeignKey('home.build', on_delete=models.SET_NULL, null=True)
    creator = models.ForeignKey('user.User', on_delete=models.CASCADE, null=True, related_name='created_tracks')
    creator_name = models.CharField(default='', max_length=200)
    default = models.BooleanField(default=False)
    details = models.CharField(default='', max_length=2000)
    label = models.CharField(default='', max_length=200)
    long_name = models.CharField(default='', max_length=300)
    public = models.BooleanField(default=False)
    subscribers = models.ManyToManyField('user.User')
    track_type = models.CharField(default='', max_length=100)

    def to_dict(self):
        return {'build': self.build.long_name, 'creator_id': self.creator_id, 'default': self.deafult,
                'details': self.details, 'id': self.id, 'label': self.label, 'track_type': self.track_type}

    def get_elements_by_coordinate(self, chromosome, min_coordinate, max_coordinate):
        if self.track_type == 'enhancer':
            element_objects = self.enhancers
        elif self.track_type == 'cnv':
            element_objects = self.variants
        elif self.track_type == 'tad':
            element_objects = self.tads
        elif self.track_type == 'other':
            element_objects = self.elements

        if self.track_type == 'cnv':
            element_objects = element_objects.filter(chromosome=chromosome) \
                .filter(Q(outer_start__range=(min_coordinate, max_coordinate)) |
                        Q(outer_end__range=(min_coordinate, max_coordinate)) |
                        Q(outer_start__lte=min_coordinate, outer_end__gte=max_coordinate)) \
                .order_by('outer_start').all()
        else:
            element_objects = element_objects.filter(chromosome=chromosome) \
                .filter(Q(start__range=(min_coordinate, max_coordinate)) |
                        Q(end__range=(min_coordinate, max_coordinate)))
        elements = [element.to_dict() for element in element_objects]

        track_dict = self.to_dict()
        track_dict['elements'] = elements
        return track_dict
