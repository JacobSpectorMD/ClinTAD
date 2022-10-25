from django.db import models


class UT(models.Model):
    track = models.ForeignKey('home.Track', on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='tracks')
    active = models.BooleanField(default=False)
    color = models.CharField(default='#0000FF', max_length=20)

    class Meta:
        unique_together = (("track", "user"),)

    def to_dict(self):
        return {'active': self.active, 'label': self.track.label, 'build': self.track.build.long_name,
                'details': self.track.details, 'id': self.id, 'ut_id': self.id, 'track_id': self.track.id,
                'track_type': self.track.track_type, 'color': self.color, 'user': self.track.creator.name}

    def remove(self, request):
        track = self.track
        self.delete()
        if request.user in track.subscribers.all():
            track.subscribers.remove(request.user)

    def edit(self, request):
        color = request.POST.get('color')
        active = request.POST.get('active')
        if color:
            self.color = color
        if active == 'false':
            self.active = False
        else:
            if self.track.track_type == 'TAD':
                request.user.track_manager.default_tads = False
                request.user.track_manager.save()
                uts = UT.objects.filter(user=request.user, track__track_type='TAD').all()
                for ut in uts:
                    ut.active = False
                    ut.save()
            self.active = True
        self.save()
