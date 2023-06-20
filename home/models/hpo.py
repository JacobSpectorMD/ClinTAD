from django.db import models


class HPO(models.Model):
    hpo_id = models.IntegerField(default=-1)
    name = models.CharField(default='', max_length=500)
    definition = models.CharField(default='', max_length=2100)
    comment = models.CharField(default='', max_length=2100)
    weight = models.FloatField(default=-1)

    def to_dict(self):
        return {'hpo_id': self.hpo_id, 'name': self.name, 'definition': self.definition, 'comment': self.comment,
                'weight': self.weight}
