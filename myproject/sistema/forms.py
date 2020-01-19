from django import forms
from .models import Miembro,Grupo,Tipo_Reunion,Reunion,Domicilio,Asistencia,Tipo_Telefono,Telefono,Horario_Disponible,Encuesta,Pregunta,Respuesta
from .models import Barrio,Localidad,Provincia,Estado_Civil,Telefono_Contacto,Configuracion,Tipo_Pregunta,Tipo_Encuesta

class GrupoForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
            super(GrupoForm, self).__init__(*args, **kwargs)
            self.fields['miembro'].queryset = Miembro.objects.filter(borrado=False)
             
    class Meta:
        model=Grupo
        fields=['nombre','miembro','sexo','desde','hasta']
        widgets={
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'miembro':forms.CheckboxSelectMultiple(),
            'desde':forms.TextInput(attrs={'class':'form-control','type':'number','min':'0'}),
            'hasta':forms.TextInput(attrs={'class':'form-control','type':'number','max':'100'})
        }
        
class Tipo_ReunionForm(forms.ModelForm):
    class Meta:
        model=Tipo_Reunion
        fields=['nombre','descripcion']

class Estado_CivilForm(forms.ModelForm):
    class Meta:
        model=Estado_Civil
        fields=['estado']
        widgets={
            'estado':forms.TextInput(attrs={'class':'form-control'}),
        }

class ReunionForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
            super(ReunionForm, self).__init__(*args, **kwargs)
            self.fields['grupo'].queryset = Grupo.objects.filter(borrado=False)
            self.fields['tipo_reunion'].queryset = Tipo_Reunion.objects.filter(borrado=False)
             
    class Meta:
        model=Reunion
        fields=['nombre','tipo_reunion','grupo']
        labels={
            'nombre':'Nombre'
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control','onkeypress':'return Solo_Texto(event);'}),
        }

class BarrioForm(forms.ModelForm):
    class Meta:
        model=Barrio
        fields=['barrio']
        widgets={
            'barrio':forms.Select(attrs = {'class' : 'form-control' }),
        } 

class LocalidadForm(forms.ModelForm):
    class Meta:
        model=Localidad
        fields=['localidad']
        widgets={
            'localidad':forms.Select(attrs = {'class' : 'form-control'}),
        } 
    
class ProvinciaForm(forms.ModelForm):
    class Meta:
        model=Provincia
        fields=['provincia']   
        widgets={
            'provincia':forms.Select(attrs = {'class' : 'form-control' }),
        }   
    
class DomicilioForm(forms.ModelForm):
    class Meta:
        model=Domicilio
        fields=['calle','nro','mz','departamento','piso']
        widgets={
            'calle':forms.TextInput(attrs={'class':'form-control'}),
            'nro':forms.TextInput(attrs={'class':'form-control'}),
            'mz':forms.TextInput(attrs={'class':'form-control'}),
            'departamento':forms.TextInput(attrs={'class':'form-control'}),
            'piso':forms.TextInput(attrs={'class':'form-control'})
        }

class MiembroForm(forms.ModelForm):
    class Meta:
        model = Miembro
        fields = ['nombre','apellido','dni','fecha_nacimiento' ,'cant_hijo','trabaja','sexo','correo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class':'form-control'}),
            'apellido':forms.TextInput(attrs={'class':'form-control'}),
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
        fields=['miembro','reunion','fecha']

class Tipo_TelefonoForm(forms.ModelForm): 
    class Meta:
        model = Tipo_Telefono
        fields = ['tipo','empresa']
        
class TelefonoForm(forms.ModelForm):
    class Meta:
        model = Telefono
        fields = ['prefijo','numero','whatsapp']

class Telefono_ContactoForm(forms.ModelForm):
    class Meta:
        model=Telefono_Contacto
        fields=['miembro']
        widgets={
           'miembro':forms.Select(attrs={'class':'form-control '})
        }

class Horario_DisponibleForm(forms.ModelForm): 
    class Meta:
        model = Horario_Disponible
        fields = ['dia','desde','hasta']
        widgets={
            'dia':forms.Select(attrs={'class':'form-control '}),
            'desde': forms.TimeInput(attrs={'class':'form-control '}),
            'hasta':forms.TimeInput(attrs={'class':'form-control '})
        }

class Tipo_PreguntaForm(forms.ModelForm):
    class Meta:
        model = Tipo_Pregunta
        fields = ['tipo']

class Tipo_EncuestaForm(forms.ModelForm):
    class Meta:
        model = Tipo_Encuesta
        fields = ['tipo']

class EncuestaForm(forms.ModelForm): 
    class Meta:
        model = Encuesta
        fields = ['envio','cantidad','tipo']

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ['descripcion','tipo','tipo_encuesta']
        widgets = {
            'descripcion':forms.TextInput(attrs={'class':'form-control'}),
        }

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ['descripcion','puntaje','pregunta']

class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model= Configuracion
        fields = ['titulo','telefono','direccion']
        widgets={
            'titulo':forms.TextInput(attrs={'class':'form-control'}),
            'telefono':forms.TextInput(attrs={'class':'form-control'}),
            'direccion':forms.TextInput(attrs={'class':'form-control'}),
            #'logo':forms.TextInput(attrs={'class':'form-control'}),
        }


