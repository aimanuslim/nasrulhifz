from django import forms
from django.forms import formset_factory

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields


    def __init__(self , *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg m-4 custom-size'
            if visible.field == self.fields['username']:
                visible.field.widget.attrs['placeholder'] = 'Username'

            if visible.field == self.fields['password1']:
                visible.field.widget.attrs['placeholder'] = 'Enter Password'

            if visible.field == self.fields['password2']:
                visible.field.widget.attrs['placeholder'] = 'Reenter Password'








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
            'name': 'lower_bound',
            'id': 'min-limit-input',
        }), required=False)

    max_range = forms.IntegerField(min_value=1, max_value=288, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Upper Bound',
            'name': 'upper_bound',
            'id': 'max-limit-input',
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


