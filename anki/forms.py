from django import forms

class PostForm(forms.Form):
    data = forms.CharField()

class OneByOne(forms.Form):
    foreign = forms.CharField(label='暗記したい単語', required=False)
    japanese = forms.CharField(label='意味、訳', required=False)
    sentence = forms.CharField(label='例文（この欄は任意です）', required=False)

class Json(forms.Form):
    json = forms.CharField(label='以下の例と同じ形式で入力してください', widget=forms.Textarea(attrs={'cols': '100', 'rows': '5'}), required=False)