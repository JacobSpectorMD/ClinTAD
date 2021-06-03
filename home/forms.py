from django import forms


class SingleForm(forms.Form):
    coordinates = forms.CharField(required=True, label="Coordinates: ")
    phenotypes = forms.CharField(required=False, label="Phenotypes: ")


class MultiLineForm(forms.Form):
    multiple = forms.CharField(widget=forms.Textarea(), label ="", strip=False)


class HPOLookup(forms.Form):
    lookup = forms.CharField()
