from django.db import models


class HPO(models.Model):
    hpoid = models.IntegerField(default=-1)
    name = models.CharField(default='', max_length=500)
    definition = models.CharField(default='', max_length=2100)
    comment = models.CharField(default='', max_length=2100)
    weight = models.FloatField(default=-1)

    def to_dict(self):
        return {'hpoid': self.hpoid, 'name': self.name, 'definition': self.definition, 'comment': self.comment,
                'weight': self.weight}
