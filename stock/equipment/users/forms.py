from django import forms


class LoginUserForm(forms.Form):
    username = forms.CharField(
                               max_length=20,
                               label='Логин',
                               widget=forms.TextInput(
                                   attrs={'class': 'form-input'}))
    password = forms.CharField(
        max_length=20,
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}))
