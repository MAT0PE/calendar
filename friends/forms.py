from django import forms
from django.core.validators import MinLengthValidator

class ChatForm(forms.Form):
    text = forms.CharField(initial='', widget=forms.Textarea(attrs={'cols': '1', 'rows': '1'}))

class ProfileForm(forms.Form):
    name = forms.CharField(label='ユーザーネーム', max_length=20, validators=[MinLengthValidator(1)])
    message = forms.CharField(label='一言コメント', required=False, widget=forms.Textarea(attrs={'cols': '60', 'rows': '2'}))
    ranking = forms.BooleanField(label='ランキングに掲載する', required=False)
