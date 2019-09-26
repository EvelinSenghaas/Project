from django import forms
from .models import Miembro,Grupo,Tipo_Reunion,Reunion,Domicilio,Asistencia,Tipo_Telefono,Telefono,Horario_Disponible,Encuesta,Pregunta,Respuesta

class GrupoForm(forms.ModelForm): 
    class Meta:
        model=Grupo
        fields=['nombre','miembro']

class Tipo_ReunionForm(forms.ModelForm):
    class Meta:
        model=Tipo_Reunion
        fields=['nombre','descripcion']

class ReunionForm(forms.ModelForm):
    class Meta:
        model=Reunion
        fields=['nombre','fecha','hora','tipo_reunion','grupo']

class DomicilioForm(forms.ModelForm):
    class Meta:
        model=Domicilio
        fields=['calle','nro','mz','barrio','localidad','provincia','departamento','piso']

class MiembroForm(forms.ModelForm):
    class Meta:
        model = Miembro
        fields = ['nombre','apellido','tipo_dni','dni','nacionalidad','fecha_nacimiento','estado_civil','cant_hijo','trabaja','correo','horario_disponible']

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
        fields = ['prefijo','numero','whatsapp','tipo_telefono']

class Horario_DisponibleForm(forms.ModelForm): 
    class Meta:
        model = Horario_Disponible
        fields = ['dia','desde','hasta']
        widgets={
            'dia':forms.Select(attrs={'class':'form-control col-md-20'}),
            'desde': forms.TextInput(attrs={'class':'form-control col-md-20'}),
            'hasta':forms.TextInput(attrs={'class':'form-control col-md-20'})
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



