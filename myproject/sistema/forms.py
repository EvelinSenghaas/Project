from django import forms
from .models import Miembro,Grupo,Tipo_Reunion,Reunion,Domicilio,Asistencia,Tipo_Telefono,Telefono,Horario_Disponible,Encuesta,Pregunta,Respuesta

class GrupoForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
            super(GrupoForm, self).__init__(*args, **kwargs)
            self.fields['miembro'].queryset = Miembro.objects.filter(borrado=False)
             
    class Meta:
        model=Grupo
        fields=['nombre','miembro']
        widgets={
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'miembro':forms.CheckboxSelectMultiple(),
        }
        
class Tipo_ReunionForm(forms.ModelForm):
    class Meta:
        model=Tipo_Reunion
        fields=['nombre','descripcion']

class ReunionForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
            super(ReunionForm, self).__init__(*args, **kwargs)
            self.fields['grupo'].queryset = Grupo.objects.filter(borrado=False)
            self.fields['tipo_reunion'].queryset = Tipo_Reunion.objects.filter(borrado=False)
             
    class Meta:
        model=Reunion
        fields=['nombre','fecha','hora','tipo_reunion','grupo','domicilio']
        labels={
            'nombre':'Nombre','fecha':'Fecha'
        }
        
class DomicilioForm(forms.ModelForm):
    class Meta:
        model=Domicilio
        fields=['calle','nro','mz','barrio','localidad','provincia','departamento','piso']
        widgets={
            'calle':forms.TextInput(attrs={'class':'form-control'}),
            'nro':forms.TextInput(attrs={'class':'form-control'}),
            'mz':forms.TextInput(attrs={'class':'form-control'}),
            'barrio':forms.TextInput(attrs={'class':'form-control'}),
            'localidad':forms.TextInput(attrs={'class':'form-control'}),
            'provincia':forms.TextInput(attrs={'class':'form-control'}),
            'departamento':forms.TextInput(attrs={'class':'form-control'}),
            'piso':forms.TextInput(attrs={'class':'form-control'})
        }

class MiembroForm(forms.ModelForm):
    class Meta:
        model = Miembro
        fields = ['nombre','apellido','tipo_dni','dni','fecha_nacimiento','estado_civil','cant_hijo','trabaja','sexo','correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'apellido':forms.TextInput(attrs={'class':'form-control'}),
            'tipo_dni':forms.Select(attrs = {'class' : 'form-control' }),
            'dni':forms.TextInput(attrs={'class':'form-control'}),
            'fecha_nacimiento':forms.DateInput(attrs={'class':'form-control f_nac'}),
            'cant_hijo':forms.TextInput(attrs={'class':'form-control'}), #no es tan text....
            #'trabaja': forms.BooleanField(required=True),
            'correo':forms.EmailInput(attrs={'class':'form-control'}),
            #'horario_disponible': grrr
        }

class AsistenciaForm(forms.ModelForm):
    class Meta:
        model=Asistencia
        fields=['presente','justificacion','miembro','reunion']

class Tipo_TelefonoForm(forms.ModelForm): 
    class Meta:
        model = Tipo_Telefono
        fields = ['tipo','empresa']
        
class TelefonoForm(forms.ModelForm):
    class Meta:
        model = Telefono
        fields = ['prefijo','numero','whatsapp']
        

class Horario_DisponibleForm(forms.ModelForm): 
    class Meta:
        model = Horario_Disponible
        fields = ['dia','desde','hasta']
        widgets={
            'dia':forms.Select(attrs={'class':'form-control '}),
            'desde': forms.TimeInput(attrs={'class':'form-control '}),
            'hasta':forms.TimeInput(attrs={'class':'form-control '})
        }

class EncuestaForm(forms.ModelForm): 
    class Meta:
        model = Encuesta
        fields = ['fecha_envio','miembro']

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['descripcion','encuesta']

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['descripcion','puntaje','pregunta']



