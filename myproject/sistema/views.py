from django.shortcuts import render,redirect
from .forms import MiembroForm,Tipo_ReunionForm,ReunionForm,AsistenciaForm,Horario_DisponibleForm,Tipo_TelefonoForm
from .forms import TelefonoForm,EncuestaForm,PreguntaForm,RespuestaForm,GrupoForm
def Home(request):
    return render(request,'index.html')


def crearGrupo(request):
    if request.method == 'POST':
        grupo_form = GrupoForm(request.POST)
        if grupo_form.is_valid():
            grupo_form.save()
            return redirect('home')
    else:
        grupo_form=GrupoForm()
    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form})

def crearMiembro(request):
    if request.method == 'POST':
        miembro_form=MiembroForm(request.POST)
        if miembro_form.is_valid():
            miembro_form.save()
            return redirect('home')
    
    else:
        miembro_form=MiembroForm()

    return render(request,'sistema/crearMiembro.html',{'miembro_form':miembro_form})

def crearTipo_Reunion(request):
    if request.method == 'POST':
        tipo_reunion_form= Tipo_ReunionForm(request.POST)
        if tipo_reunion_form.is_valid():
            tipo_reunion_form.save()
            return redirect('home')
    else:
        tipo_reunion_form=Tipo_ReunionForm()
    return render(request,'sistema/crearTipo_Reunion.html',{'tipo_reunion_form':tipo_reunion_form})

def crearReunion(request):
    if request.method == 'POST':
        reunion_form=ReunionForm(request.POST)
        if reunion_form.is_valid():
            reunion_form.save()
            return redirect('home')
    else:
        reunion_form=ReunionForm()
    return render(request,'sistema/crearReunion.html',{'reunion_form':reunion_form})

def agregarAsistencia(request):
    if request.method == 'POST':
        asistencia_form=AsistenciaForm(request.POST)
        if asistencia_form.is_valid():
            asistencia_form.save()
            return redirect('home')
    else:
        asistencia_form=AsistenciaForm()
    return render(request,'sistema/agregarAsistencia.html',{'asistencia_form':asistencia_form})

def agregarTipo_Telefono(request):
    if request.method == 'POST':
        tipo_telefono_form = Tipo_TelefonoForm(request.POST)
        if tipo_telefono_form.is_valid():
            tipo_telefono_form.save()
            return redirect('home')
    else:
        tipo_telefono_form = Tipo_TelefonoForm()
    return render(request,'sistema/agregarTipo_Telefono.html',{'tipo_telefono_form':tipo_telefono_form})   

def agregarTelefono(request):
    if request.method == 'POST':
        telefono_form = TelefonoForm(request.POST)
        if telefono_form.is_valid():
            telefono_form.save()
            return redirect('home')
    else:
        telefono_form=TelefonoForm()
    return render(request,'sistema/agregarTelefono.html',{'telefono_form':telefono_form})

def agregarHorario_Disponible(request):
    if request.method == 'POST':
        horario_disponible_form = Horario_DisponibleForm(request.POST)
        if horario_disponible_form.is_valid():
            horario_disponible_form.save()
            return redirect('home')
    else:
        horario_disponible_form = Horario_DisponibleForm()
    return render(request,'sistema/agregarHorario_Disponible.html',{'horario_disponible_form':horario_disponible_form})

def agregarEncuesta(request):
    if request.method == 'POST':
        encuesta_form=EncuestaForm(request.form)
        if encuesta_form.is_valid():
            encuesta_form.save()
            return redirect('home')
    else:
        encuesta_form=EncuestaForm()
    return render(request,'sistema/agregarEncuesta.html',{'encuesta_form':encuesta_form})

def agregarPregunta(request):
    if request.method =='POST':
        pregunta_form=PreguntaForm(request.POST)
        if pregunta_form.is_valid:
            pregunta_form.save()
            return redirect('home')
    else:
        pregunta_form=PreguntaForm()
    return render(request,'sistema/agregarPregunta.html',{'pregunta_form':pregunta_form})

def agregarRespuesta(request):
    if request.method == 'POST':
        respuesta_form=RespuestaForm(request.POST)
        if respuesta_form.is_valid():
            respuesta_form.save()
            return redirect('home')
    else:
        respuesta_form=RespuestaForm()
    return(request,'sistema/agregarRespuesta.html',{'respuesta_form':respuesta_form})