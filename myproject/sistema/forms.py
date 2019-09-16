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
        fields=['fecha','hora','tipo_reunion']

class DomicilioForm(forms.ModelForm):
    class Meta:
        model=Domicilio
        fields=['calle','nro','barrio','localidad','provincia','reunion']

class MiembroForm(forms.ModelForm):
    class Meta:
        model = Miembro
        fields = ['dni','nombre','apellido','nacionalidad','fecha_nacimiento','estado_civil','cant_hijo','trabaja','domicilio','correo']

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
        fields = ['prefijo','numero','whatsapp','miembro','tipo_telefono']

class Horario_DisponibleForm(forms.ModelForm): 
    class Meta:
        model = Horario_Disponible
        fields = ['dia','hora','miembro']

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



