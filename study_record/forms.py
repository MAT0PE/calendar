from django import forms
from django.core.validators import MinLengthValidator
import datetime

class RecordForm(forms.Form):
    start = forms.DateTimeField(label='開始時刻', widget=forms.DateTimeInput(attrs={"type": "datetime-local", "value": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')}),
    input_formats=['%Y-%m-%dT%H:%M'], required=False)
    end = forms.DateTimeField(label='開始時刻', widget=forms.DateTimeInput(attrs={"type": "datetime-local", "value": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')}),
    input_formats=['%Y-%m-%dT%H:%M'], required=False)
    subject = forms.CharField(label='内容', max_length=20, required=False)

class DetailForm(forms.Form):
    start = forms.DateTimeField(label='表示開始日', widget=forms.DateInput(attrs={"type": "date"}), 
    input_formats=['%Y-%m-%d'], help_text='この日付から一週間の勉強記録が表示されます')

class FirstSettingsForm(forms.Form):
    name = forms.CharField(label='ユーザーネーム', max_length=20, validators=[MinLengthValidator(1)])
    ranking = forms.BooleanField(label='ランキングに掲載する')