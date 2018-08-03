from django import forms

class HifzForm(forms.Form):
	surah_number = forms.IntegerField(min_value=1, max_value=114)
	ayat_number = forms.IntegerField(min_value=0, max_value=288)

