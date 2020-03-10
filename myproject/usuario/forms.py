from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from sistema.models import Rol

class FormularioLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(FormularioLogin, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Usuario'

        self.fields['password'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['placeholder'] = 'Contraseña'

class CustomUserCreationForm(UserCreationForm):
    def __init__(self,*args, **kwargs):
            super(CustomUserCreationForm, self).__init__(*args, **kwargs)
            self.fields['rol'].queryset = Rol.objects.filter(borrado=False) 
    class Meta:
        model = CustomUser
        fields = ('username', 'miembro', 'email','rol')
        widgets={
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'miembro': forms.Select(attrs={'class':'form-control','id':'id_miembro'}),
            'rol': forms.Select(attrs={'class':'form-control','id':'id_rol'}),
            'email':forms.EmailInput(attrs={'class':'form-control'}),
        }