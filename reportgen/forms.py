from django import forms
from reportgen.models import Finding


class FindingForm(forms.Form):
    engagement_name = forms.CharField(label="Report Name: ", max_length=100)
