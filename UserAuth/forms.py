from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    def clean_password2(self):
        pass_1 = self.cleaned_data.get('password1')
        pass_2 = self.cleaned_data.get('password2')

        if pass_1 != pass_2:
            self._errors['password2'] = self.error_class([ 
                'Пароли не совпадают']) 

        if len(pass_1) < 6:
            self._errors['password1'] = self.error_class([ 
                'Пароль слишком короткий. Минимальная длина пароля 6 символов']) 

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        if username and password:
            if not user:   
                raise forms.ValidationError("This user does not exist")
            if not user.check_password(password):
                raise forms.ValidationError("Incorrect password")
            if not user.is_active:
                raise forms.ValidationError("This user is not longer active")
        return super(UserLoginForm, self).clean()