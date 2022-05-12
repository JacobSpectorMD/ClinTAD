from django.db import models


class Variant(models.Model):
    accession = models.CharField(default='', max_length=200)
    build = models.ForeignKey('home.Build', null=True, on_delete=models.SET_NULL)
    chromosome = models.ForeignKey('home.Chromosome', related_name='variants', on_delete=models.CASCADE)
    frequency = models.FloatField(default=-1)
    inner_end = models.IntegerField(default=-1)
    inner_start = models.IntegerField(default=-1)
    outer_end = models.IntegerField(default=-1)
    outer_start = models.IntegerField(default=-1)
    sample_size = models.IntegerField(default=-1)
    subtype = models.CharField(default='', max_length=5)
    study = models.CharField(default='', max_length=300)
    track = models.ForeignKey('home.Track', null=True, on_delete=models.CASCADE, related_name='variants')

    def to_dict(self):
        return {'chromosome': self.chromosome.number, 'outer_start': self.outer_start, 'inner_start': self.inner_start,
                'inner_end': self.inner_end, 'outer_end': self.outer_end, 'subtype': self.subtype,
                'accession': self.accession, 'study': self.study, 'sample_size': self.sample_size,
                'frequency': self.frequency}