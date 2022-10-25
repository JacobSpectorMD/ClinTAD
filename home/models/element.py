from django.db import models


class Element(models.Model):
    build = models.ForeignKey('home.Build', on_delete=models.SET_NULL, null=True)
    chromosome = models.ForeignKey('home.Chromosome', on_delete=models.CASCADE)
    details = models.CharField(default='', max_length=2000)
    end = models.IntegerField(default=-1, null=True)
    label = models.CharField(default='', max_length=200)
    start = models.IntegerField(default=-1)
    track = models.ForeignKey('home.Track', on_delete=models.CASCADE, related_name='elements')

    def to_dict(self):
        return {'chromosome': self.chromosome.number, 'start': self.start, 'end': self.end, 'label': self.label,
                'details': self.details}