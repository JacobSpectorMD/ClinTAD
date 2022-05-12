from django.db import models


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
        return {'build': self.build.long_name, 'creator_id': self.creator_id, 'details': self.details, 'id': self.id,
                'label': self.label, 'track_type': self.track_type}
