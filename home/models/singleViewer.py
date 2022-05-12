from django.db import models


class SingleViewer(models.Model):
    ip_address = models.CharField(default='', max_length=100)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.ip_address
