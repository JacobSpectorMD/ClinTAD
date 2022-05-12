from django.db import models


class Enhancer(models.Model):
    build = models.ForeignKey('home.Build', on_delete=models.SET_NULL, null=True)
    chromosome = models.ForeignKey('home.Chromosome', on_delete=models.CASCADE)
    end = models.IntegerField(default=-1)
    start = models.IntegerField(default=-1)
    track = models.ForeignKey('home.Track', on_delete=models.CASCADE, null=True, related_name='enhancers')
    vista_element = models.IntegerField(default=-1)

    def to_dict(self):
        return {'chromosome': str(self.chromosome), 'start': self.start, 'end': self.end,
                'vista_element': self.vista_element}
