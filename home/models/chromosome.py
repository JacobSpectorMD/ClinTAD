from django.db import models


class Chromosome(models.Model):
    build = models.ForeignKey('home.Build', on_delete=models.SET_NULL, null=True)
    number = models.CharField(default='', max_length=2)
    length = models.IntegerField(default=-1)

    def __str__(self):
        return 'Chromosome ' + str(self.number)
