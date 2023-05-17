from django.db import models


class UT(models.Model):
    track = models.ForeignKey('home.Track', on_delete=models.CASCADE)
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='tracks')
    active = models.BooleanField(default=False)
    color = models.CharField(default='#0000FF', max_length=20)

    class Meta:
        unique_together = (("track", "user"),)

    def to_dict(self):
        t = self.track
        return {'active': self.active, 'article_name': t.article_name, 'author_last_name': t.author_last_name,
                'creator': self.track.creator.name, 'label': self.track.label, 'build': self.track.build.long_name,
                'details': self.track.details, 'id': self.id, 'pubmed_id': t.pubmed_id, 'ut_id': self.id,
                'track_id': self.track.id, 'track_type': self.track.track_type, 'year': t.year, 'color': self.color,
                'user': self.track.creator.name}

    def remove(self, request):
        """
            Removes the track from the user's list of tracks by deleting the UT object. If the track was originally
            created by the requesting user and the track is not public, also delete the related track object.
        """
        track = self.track
        if track.creator == request.user and not track.public:
            track.delete()
        elif request.user == self.user:  # Only allow people to delete their own tracks
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
