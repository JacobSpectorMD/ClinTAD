from django.db import models


class Gene(models.Model):

    build = models.ForeignKey('home.Build', null=True, on_delete=models.SET_NULL)
    chromosome = models.ForeignKey('home.Chromosome', on_delete=models.CASCADE)
    end = models.IntegerField(default=-1)
    ensembl_id = models.IntegerField(default=-1)
    hpos = models.ManyToManyField('home.HPO')
    name = models.CharField(default='', max_length=100)
    omims = models.ManyToManyField('home.Omim', related_name='genes')
    start = models.IntegerField(default=-1)
    symbols = models.IntegerField(default=0)
    updated = models.BooleanField(default=False)

    def to_dict(self):
        return {'chromosome': self.chromosome, 'name': self.name, 'start': self.start, 'end': self.end,
                'hpos': [hpo.to_dict for hpo in self.hpos]}
