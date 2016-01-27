# -*- coding: utf-8 -*-

from django import forms


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a image(optional, only uspace_50 now)',
        required=False,
    )
    newaddr = forms.CharField(
        label='New Address (required)',
        max_length=200,
        required=True,
    )
    oldaddr = forms.CharField(
        label='Old Address (optional)',
        max_length=200,
        required=False,
    )
    resulttype = forms.ChoiceField(
        label='Result Display Type',
        choices=(('html', 'html'), ('json', 'json')),
    )
    latitude = forms.FloatField(
        label='latitude (optional)',
        required=False,
    )
    longitude = forms.FloatField(
        label='longitude (optional)',
        required=False,
    )

