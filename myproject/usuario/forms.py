from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class FormularioLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
      super(FormularioLogin, self).__init__(*args, **kwargs)
      self.fields['username'].widget.attrs['class'] = 'form-control'
      self.fields['username'].widget.attrs['placeholder'] = 'Usuario'

      self.fields['password'].widget.attrs['class'] = 'form-control'
      self.fields['password'].widget.attrs['placeholder'] = 'Contraseña'

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'miembro', 'email','rol')