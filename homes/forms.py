from django import forms


class AddCaregiverForm(forms.Form):
    email = forms.EmailField()
