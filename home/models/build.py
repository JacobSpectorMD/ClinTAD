from django.db import models


class Build(models.Model):
    """
        This model is used to represent genome builds. Only objects from a single build should be displayed at one
        time.
    """
    long_name = models.CharField(default='', max_length=200)
    name = models.CharField(default='', max_length=100, unique=True)
