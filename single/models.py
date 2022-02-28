from django.db import models


class Case(models.Model):
    comments = models.CharField(max_length=600, blank=True, default='')
    coordinates = models.CharField(max_length=40)
    phenotypes = models.CharField(max_length=300, blank=True, default='')
    submission_date = models.DateTimeField(auto_now_add=True)
    submitter_email = models.CharField(max_length=62)
    submitter_name = models.CharField(max_length=90)

    def __str__(self):
        return ", ".join([self.name_text, self.coordinates_text, self.phenotypes_text, self.comments_text])
        # return self.name_text +", " + self.email_text + ", " + self.coordinates_text + ", " + self.phenotypes_text + ", " + self.comments_text
