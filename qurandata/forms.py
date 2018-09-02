from django import forms
from django.forms import formset_factory

class HifzForm(forms.Form) :
    surah_number = forms.IntegerField(min_value=1, max_value=114, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Surah Number',
            'name': 'surah_number',
            'id': 'surah-number-form'
        }))
    ayat_number = forms.IntegerField(min_value=1, max_value=288, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ayat Number',
            'name': 'ayat_number',
            'id': 'ayat-number-input',
        }), required=False)

    min_range = forms.IntegerField(min_value=1, max_value=288, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Lower Bound',
            'name': 'lower_bound'
        }), required=False)

    max_range = forms.IntegerField(min_value=1, max_value=288, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Upper Bound',
            'name': 'upper_bound'
        }), required=False)








class WordIndexForm(forms.Form):
    index = forms.IntegerField(
        label='Word Index',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Word Index',
            'aria-label': 'Word Index',
            'aria-describedby': 'basic-addon2',
            'name': 'index',

            }),
        min_value=1,

        )

WordIndexFormSet = formset_factory(WordIndexForm, extra=1)
