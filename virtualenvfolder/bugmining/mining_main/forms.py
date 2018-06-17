from django import forms

class ReleaseForm(forms.Form):
    release_number = forms.CharField(label='Release Number', max_length=100)

class ClassifierForm(forms.Form):
    release_number = forms.CharField(label='Release Number', max_length=100)
    metrics = forms.CharField(label='Metrics', max_length=100)
