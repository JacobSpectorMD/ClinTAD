from django.db import models
from user.models import User


class Chromosome(models.Model):
    number = models.CharField(default='', max_length=2)
    length = models.IntegerField(default=-1)

    def __str__(self):
        return 'Chromosome '+str(self.number)


class Omim(models.Model):
    hpos = models.ManyToManyField('home.HPO', related_name='omims')
    omim_number = models.IntegerField(default=-1)
    title = models.CharField(default='', max_length=500)

    autosomal_dominant = models.BooleanField(default=False)
    autosomal_recessive = models.BooleanField(default=False)
    digenic = models.BooleanField(default=False)
    digenic_dominant = models.BooleanField(default=False)
    digenic_recessive = models.BooleanField(default=False)
    mitochondrial = models.BooleanField(default=False)
    multifactorial = models.BooleanField(default=False)
    x_linked = models.BooleanField(default=False)
    x_linked_dominant = models.BooleanField(default=False)
    x_linked_recessive = models.BooleanField(default=False)
    y_linked = models.BooleanField(default=False)


class HPO(models.Model):
    hpoid = models.IntegerField(default=-1)
    name = models.CharField(default='', max_length=500)
    definition = models.CharField(default='', max_length=2100)
    comment = models.CharField(default='', max_length=2100)
    weight = models.FloatField(default=-1)

    def to_dict(self):
        return {'hpoid': self.hpoid, 'name': self.name, 'definition': self.definition, 'comment': self.comment,
                'weight': self.weight}


class Gene(models.Model):
    chromosome = models.ForeignKey(Chromosome, on_delete=models.CASCADE)
    end = models.IntegerField(default=-1)
    ensembl_id = models.IntegerField(default=-1)
    hpos = models.ManyToManyField(HPO)
    name = models.CharField(default='', max_length=100)
    omims = models.ManyToManyField('home.Omim', related_name='genes')
    start = models.IntegerField(default=-1)
    symbols = models.IntegerField(default=0)

    def to_dict(self):
        return {'chromosome': self.chromosome, 'name': self.name, 'start': self.start, 'end': self.end,
                'hpos': [hpo.to_dict for hpo in self.hpos]}


class TAD(models.Model):
    chromosome = models.ForeignKey(Chromosome, on_delete=models.CASCADE)
    start = models.IntegerField(default=-1)
    end = models.IntegerField(default=-1)

    def to_dict(self):
        return {'chromosome': self.chromosome.number, 'start': self.start, 'end': self.end, 'label': '', 'details': ''}


class Enhancer(models.Model):
    chromosome = models.ForeignKey(Chromosome, on_delete=models.CASCADE)
    start = models.IntegerField(default=-1)
    end = models.IntegerField(default=-1)
    vista_element = models.IntegerField(default=-1)

    def to_dict(self):
        return {'chromosome': str(self.chromosome), 'start': self.start, 'end': self.end,
                'vista_element': self.vista_element}


class Track(models.Model):
    creator_id = models.IntegerField(default=-1)
    label = models.CharField(default='', max_length=200)
    build = models.CharField(default='', max_length=30)
    track_type = models.CharField(default='', max_length=100)
    details = models.CharField(default='', max_length=2000)
    subscribers = models.ManyToManyField(User)

    def to_dict(self):
        return {'build': self.build, 'creator_id': self.creator_id, 'details': self.details, 'label': self.label}


class Element(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='elements')
    label = models.CharField(default='', max_length=200)
    chromosome = models.ForeignKey(Chromosome, on_delete=models.CASCADE)
    start = models.IntegerField(default=-1)
    end = models.IntegerField(default=-1, null=True)
    details = models.CharField(default='', max_length=2000)

    def to_dict(self):
        return {'chromosome': self.chromosome.number, 'start': self.start, 'end': self.end, 'label': self.label,
                'details': self.details}


class UT(models.Model):  # User Track association class
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tracks')
    active = models.BooleanField(default=False)
    color = models.CharField(default='#0000FF', max_length=20)

    class Meta:
        unique_together = (("track", "user"),)

    def to_dict(self):
        return {'active': self.active, 'label': self.track.label, 'build': self.track.build,
                'details': self.track.details, 'ut_id': self.id, 'track_id': self.track.id,
                'track_type': self.track.track_type, 'color': self.color}

    def remove(self, request):
        track = self.track
        self.delete()
        if request.user in track.subscribers.all():
            track.subscribers.remove(request.user)
        subscribers = track.subscribers.all()
        if not subscribers:
            track.delete()

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


class Variant(models.Model):
    chromosome = models.ForeignKey(Chromosome, related_name='variants', on_delete=models.CASCADE)
    outer_start = models.IntegerField(default=-1)
    inner_start = models.IntegerField(default=-1)
    inner_end = models.IntegerField(default=-1)
    outer_end = models.IntegerField(default=-1)
    subtype = models.CharField(default='', max_length=5)
    accession = models.CharField(default='', max_length=200)
    study = models.CharField(default='', max_length=300)
    sample_size = models.IntegerField(default=-1)
    frequency = models.FloatField(default=-1)

    def to_dict(self):
        return {'chromosome': self.chromosome.number, 'outer_start': self.outer_start, 'inner_start': self.inner_start,
                'inner_end': self.inner_end, 'outer_end': self.outer_end, 'subtype': self.subtype,
                'accession': self.accession, 'study': self.study, 'sample_size': self.sample_size,
                'frequency': self.frequency}


class SingleViewer(models.Model):
    ip_address = models.CharField(default='', max_length=100)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.ip_address
