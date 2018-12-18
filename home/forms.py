from django import forms


class SingleForm(forms.Form):
    chromosome = forms.CharField(required=True, label="Chromosome: ")
    start = forms.CharField(required=True, label="Start: ")
    end = forms.CharField(required=True, label="End: ")
    phenotypes = forms.CharField(required=False, label="Phenotypes: ")


class MultiLineForm(forms.Form):
    multiple = forms.CharField(widget=forms.Textarea(attrs={'cols':'80'}), label ="", strip=False)


class HPOLookup(forms.Form):
    lookup = forms.CharField()
