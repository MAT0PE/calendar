from django import forms
from django.core.validators import MinLengthValidator

class LoginForm(forms.Form):
    email = forms.EmailField(help_text='有効なメールアドレスを入力してください。', label='メールアドレス')
    password = forms.CharField(label='パスワード', help_text='メールアドレスとパスワードが一致しません。')

class RegisterMailForm(forms.Form):
    email = forms.EmailField(help_text='有効なメールアドレスを入力してください。', label='メールアドレス')
    password1 = forms.CharField(label='パスワード', max_length=20)
    password2 = forms.CharField(label='パスワード（確認）', max_length=20)

class ResetMailForm(forms.Form):
    email = forms.EmailField(help_text='有効なメールアドレスを入力してください。', label='メールアドレス')

class ResetForm(forms.Form):
    email = forms.EmailField(help_text='有効なメールアドレスを入力してください。', label='メールアドレス（確認）')
    password1 = forms.CharField(label='新しいパスワード', max_length=20)
    password2 = forms.CharField(label='新しいパスワード（確認）', max_length=20)

class RegisterForm(forms.Form):
    password = forms.CharField(label='パスワード', max_length=20)