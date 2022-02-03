from django.db import models

# Create your models here.
class Case(models.Model):
    name_text = models.CharField(max_length=90)
    email_text = models.CharField(max_length=62)
    coordinates_text = models.CharField(max_length=40)
    phenotypes_text = models.CharField(max_length=300, blank=True, default='')
    comments_text = models.CharField(max_length=600, blank=True, default='')
    pub_date = models.DateTimeField(auto_now_add=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __str__(self):
        return self.name_text +", " + self.email_text + ", " + self.coordinates_text + ", " + self.phenotypes_text + ", " + self.comments_text
