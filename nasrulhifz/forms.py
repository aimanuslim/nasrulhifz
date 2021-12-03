from django import forms
from django.forms import formset_factory

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

surah_data = {1: 7, 2: 286, 3: 200, 4: 176, 5: 120, 6: 165, 7: 206, 8: 75, 9: 129, 10: 109, 11: 123, 12: 111, 13: 43, 14: 52, 15: 99, 16: 128, 17: 111, 18: 110, 19: 98, 20: 135, 21: 112, 22: 78, 23: 118, 24: 64, 25: 77, 26: 227, 27: 93, 28: 88, 29: 69, 30: 60, 31: 34, 32: 30, 33: 73, 34: 54, 35: 45, 36: 83, 37: 182, 38: 88, 39: 75, 40: 85, 41: 54, 42: 53, 43: 89, 44: 59, 45: 37, 46: 35, 47: 38, 48: 29, 49: 18, 50: 45, 51: 60, 52: 49, 53: 62, 54: 55, 55: 78, 56: 96, 57: 29, 58: 22, 59: 24, 60: 13, 61: 14, 62: 11, 63: 11, 64: 18, 65: 12, 66: 12, 67: 30, 68: 52, 69: 52, 70: 44, 71: 28, 72: 28, 73: 20, 74: 56, 75: 40, 76: 31, 77: 50, 78: 40, 79: 46, 80: 42, 81: 29, 82: 19, 83: 36, 84: 25, 85: 22, 86: 17, 87: 19, 88: 26, 89: 30, 90: 20, 91: 15, 92: 21, 93: 11, 94: 8, 95: 8, 96: 19, 97: 5, 98: 8, 99: 8, 100: 11, 101: 11, 102: 8, 103: 3, 104: 9, 105: 5, 106: 4, 107: 7, 108: 3, 109: 6, 110: 3, 111: 5, 112: 4, 113: 5, 114: 6}

class CustomUserCreationForm(UserCreationForm):
    # username = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=200)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', )

    def __init__(self , *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control form-control-lg m-4 custom-size'
            # if visible.field == self.fields['username']:
            #     visible.field.widget.attrs['placeholder'] = 'Username'

            if visible.field == self.fields['email']:
                visible.field.widget.attrs['placeholder'] = 'Email'

            if visible.field == self.fields['password1']:
                visible.field.widget.attrs['placeholder'] = 'Enter Password'

            if visible.field == self.fields['password2']:
                visible.field.widget.attrs['placeholder'] = 'Reenter Password'
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# unused
class ReviseForm(forms.Form):
    unit_number = forms.IntegerField(min_value=1, max_value=30, widget=forms.NumberInput(
        attrs={
            'type': 'number',
            'class': 'mb-4 form-control custom-size',
            'id': 'unit-number',
            'name': 'unit-number',
            'placeholder': 'Juz Number',
            'aria-describedby': 'UnitNumberWarning'
        }

        ))



class HifzForm(forms.Form) :
    surah_number = forms.IntegerField(min_value=1, max_value=114, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Surah Number',
            'name': 'surah_number',
            'id': 'surah-number-form'
        }))
    ayat_number = forms.IntegerField(min_value=1, max_value=288, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg surah-param-inputs',
            'placeholder': 'Ayat Number',
            'name': 'ayat_number',
            'id': 'ayat-number-input',
        }), required=False)

    min_range = forms.IntegerField(min_value=1, max_value=288, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg surah-param-inputs',
            'placeholder': 'Lower Bound',
            'name': 'lower_bound',
            'id': 'min-limit-input',
        }), required=False)

    max_range = forms.IntegerField(min_value=1, max_value=288, widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg surah-param-inputs',
            'placeholder': 'Upper Bound',
            'name': 'upper_bound',
            'id': 'max-limit-input',
        }), required=False)

    def clean(self):
        cleaned_data = super().clean()
        surah_number = cleaned_data.get('surah_number')
        self.fields['min_range'].max_value = surah_data.get(surah_number)
        self.fields['max_range'].max_value = surah_data.get(surah_number)

        lower_limit = cleaned_data.get('min_range')
        upper_limit = cleaned_data.get('max_range')

        if upper_limit is not None and lower_limit is not None and upper_limit < lower_limit:
            raise ValidationError("Upper limit is lower than lower limit")


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


