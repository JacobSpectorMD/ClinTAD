from django.db import models


class Case(models.Model):
    build = models.ForeignKey('home.Build', on_delete=models.SET_NULL, null=True)
    comments = models.CharField(max_length=600, blank=True, default='')
    coordinates = models.CharField(max_length=40)
    evidence = models.CharField(default='None', max_length=100)
    phenotypes = models.ManyToManyField('home.HPO')
    phenotypes_text = models.CharField(default='', max_length=1000)
    pubmed_ids = models.CharField(default='', max_length=1000)
    status = models.CharField(default='Pending', max_length=200)
    submission_date = models.DateTimeField(auto_now_add=True)
    submitter = models.ForeignKey('user.User', on_delete=models.SET_NULL, null=True)
    submitter_email = models.CharField(max_length=100)
    submitter_name = models.CharField(max_length=100)

    def __str__(self):
        return ", ".join([self.name_text, self.coordinates_text, self.phenotypes_text, self.comments_text])

    def to_dict(self):
        return {
            'build': self.build.name,
            'comments': self.comments,
            'coordinates': self.coordinates,
            'evidence': self.evidence,
            'phenotypes': self.phenotypes_text,
            'status': self.status,
            'submitter': self.submitter.name,
        }