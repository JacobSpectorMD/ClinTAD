from django.db import models


class TAD(models.Model):
    build = models.ForeignKey('home.Build', on_delete=models.SET_NULL, null=True)
    chromosome = models.ForeignKey('home.Chromosome', on_delete=models.CASCADE)
    end = models.IntegerField(default=-1)
    start = models.IntegerField(default=-1)
    track = models.ForeignKey('home.Track', on_delete=models.CASCADE, null=True, related_name='tads')

    def to_dict(self):
        return {'chromosome': self.chromosome.number, 'start': self.start, 'end': self.end, 'label': '', 'details': ''}
