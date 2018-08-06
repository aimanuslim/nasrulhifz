from django import forms
from django.forms import formset_factory

class HifzForm(forms.Form):
	surah_number = forms.IntegerField(min_value=1, max_value=114)
	ayat_number = forms.IntegerField(min_value=1, max_value=288)



class WordIndexForm(forms.Form):
	index = forms.IntegerField(
		label='Word Index',
		widget=forms.NumberInput(attrs={
			'class': 'form-control',
			'placeholder': 'Index'
			})

		)
WordIndexFormSet = formset_factory(WordIndexForm, extra=1)
