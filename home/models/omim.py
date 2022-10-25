from django.db import models


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