from django.shortcuts import render,redirect
from .forms import MiembroForm,Tipo_ReunionForm,ReunionForm,AsistenciaForm,Horario_DisponibleForm,Tipo_TelefonoForm
from .forms import TelefonoForm,EncuestaForm,PreguntaForm,RespuestaForm,GrupoForm,DomicilioForm
from .models import Miembro,Grupo,Tipo_Reunion,Reunion,Tipo_Telefono,Telefono,Domicilio,Horario_Disponible
from datetime import date
import datetime
from django.contrib import messages
from django.core import serializers
import json
from django.http import HttpResponse
from django.http import JsonResponse


def Home(request):
    return render(request,'sistema/index.html')

def Asistencia(request):
    if request.method == 'POST':
        return redirect('home')
    else:
        return render(request,'sistema/index_asistencia.html')

def crearGrupo(request):
    if request.method == 'POST':
        grupo_form = GrupoForm(request.POST)
        if grupo_form.is_valid():
            grupo_form.save()
            return redirect('/sistema/listarGrupo')
    else:
        grupo_form=GrupoForm()
    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form})

def listarGrupo(request):
    grupos = Grupo.objects.filter(borrado=False)
    return render(request,'sistema/listarGrupo.html',{'grupos':grupos})

def editarGrupo(request,id_grupo):
    grupo = Grupo.objects.get(id_grupo=id_grupo)
    if request.method =='GET':
        grupo_form=GrupoForm(instance=grupo)
    else:
        grupo_form=GrupoForm(request.POST,instance=grupo)
        if grupo_form.is_valid():
            grupo_form.save()
        return redirect('/sistema/listarGrupo')
    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form})

def eliminarGrupo(request,id_grupo):
    grupo = Grupo.objects.get(id_grupo=id_grupo)
    grupo.borrado=True
    grupo.save()
    return redirect('/sistema/listarGrupo')

def listarMiembro(request):
    miembros = Miembro.objects.filter(borrado=False)
    for miembro in miembros:        
        miembro.fecha_nacimiento = miembro.edad(miembro.fecha_nacimiento)
    return render(request,'sistema/listarMiembro.html',{'miembros':miembros})

def crearMiembro(request):
    if request.method == 'POST':

        miembro_form=MiembroForm(request.POST)
        miembro=miembro_form.save(commit=False)

        domicilio_form=DomicilioForm(request.POST)
        domicilio=domicilio_form.save()

        horario_form=Horario_DisponibleForm(request.POST)
        horario=horario_form.save()
        
        if Tipo_TelefonoForm(request.POST)!= None:
            tipo_telefono_form=Tipo_TelefonoForm(request.POST)
            tipo_telefono=tipo_telefono_form.save()
            telefono_form=TelefonoForm(request.POST)
            telefono=telefono_form.save(commit=False)
            telefono.tipo_telefono=tipo_telefono
            telefono.save()

        fecha = datetime.datetime.strptime(str(miembro.fecha_nacimiento), '%Y-%m-%d')
        if fecha.date() > datetime.date.today():
            print(fecha.date())
            messages.error(request, 'fecha de nacimiento incorrecta')
            return render(request,'sistema/editarMiembro.html',{'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})
        
        else:
            miembro.domicilio=domicilio
            miembro.horario_disponible=horario
            if  telefono != None:
                miembro.telefono=telefono
            miembro.nombre=miembro.nombre.capitalize()
            miembro.apellido=miembro.apellido.upper()
            miembro.save()
            return redirect('/sistema/listarMiembro')
        
    else:
        domicilio_form=DomicilioForm()
        miembro_form=MiembroForm()
        tipo_telefono_form=Tipo_TelefonoForm()
        telefono_form=TelefonoForm()
        horario_form=Horario_DisponibleForm()
        return render(request,'sistema/crearMiembro.html',{'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})

def editarMiembro(request,dni):
    miembro = Miembro.objects.get(dni= dni)
    id_domicilio=miembro.domicilio.id_domicilio
    domicilio=Domicilio.objects.get(id_domicilio=id_domicilio)

    if miembro.telefono != None:
        id_telefono=miembro.telefono.id_telefono
        telefono=Telefono.objects.get(id_telefono=id_telefono)
        id_tipo_telefono=telefono.tipo_telefono.id_tipo_telefono
        tipo_telefono=Tipo_Telefono.objects.get(id_tipo_telefono=id_tipo_telefono)
    else: 
        telefono=None
        tipo_telefono=None
    id_horario=miembro.horario_disponible.id_horario_disponible
    horario_disponible = Horario_Disponible.objects.get(id_horario_disponible=id_horario)

    if request.method == 'GET':
        miembro_form=MiembroForm(instance = miembro)
        domicilio_form=DomicilioForm(instance=domicilio)
        if miembro.telefono != None:
            tipo_telefono_form=Tipo_TelefonoForm(instance=tipo_telefono)
            telefono_form=TelefonoForm(instance=telefono)
        else:
            tipo_telefono_form=Tipo_TelefonoForm()
            telefono_form=TelefonoForm()
        horario_form=Horario_DisponibleForm(instance=horario_disponible)
    else:
        miembro_form=MiembroForm(request.POST,instance=miembro)
        domicilio_form=DomicilioForm(request.POST,instance=domicilio)
        horario_form=Horario_DisponibleForm(request.POST,instance=horario_disponible)
        telefono_form=TelefonoForm(request.POST,instance=telefono)
        tipo_telefono_form=Tipo_TelefonoForm(request.POST,instance=tipo_telefono)
        miembro=miembro_form.save(commit=False)
        
        fecha = datetime.datetime.strptime(str(miembro.fecha_nacimiento), '%Y-%m-%d')
        if fecha.date() > datetime.date.today():
            print(fecha.date())
            messages.error(request, 'fecha de nacimiento incorrecta')       
        else: 
            if tipo_telefono_form.is_valid() and telefono_form.is_valid() and horario_form.is_valid() and miembro_form.is_valid() and domicilio_form.is_valid() :
                if request.POST.get('prefijo') and request.POST.get('numero') != None:
                    tipo=tipo_telefono_form.save()
                    telefono=telefono_form.save(commit=False)
                    telefono.tipo_telefono=tipo
                    telefono.save()
                    miembro.telefono=telefono
                domicilio=domicilio_form.save()
                horario=horario_form.save()
                
                miembro.nombre=miembro.nombre.capitalize()
                miembro.apellido=miembro.apellido.upper()
                miembro.save()
                return redirect('/sistema/listarMiembro')

        '''else:
            if request.POST.get('prefijo') and request.POST.get('numero') != None:
                tipo=request.POST.get('tipo')
                empresa=request.POST.get('empresa')
                prefijo=request.POST.get('prefijo')
                numero=request.POST.get('numero')
                whatsapp=request.POST.get('whatsapp')
                tipo_telefono_form=Tipo_Telefono(tipo=tipo,empresa=empresa)
                telefono_form=Telefono(prefijo=prefijo,numero=numero,whatsapp=whatsapp,tipo_telefono=tipo_telefono_form)
        

            telefono_form.tipo_telefono=tipo
            miembro_form.telefono=telefono
            miembro_form.horario_disponible=horario
            miembro_form.domicilio=domicilio'''
                     
        

    return render(request,'sistema/editarMiembro.html',{'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})

def eliminarMiembro(request,dni):
    miembroo = Miembro.objects.get(dni=dni)
    if Grupo.objects.filter(miembro = miembroo,borrado=False).exists():
        print('lina pone un msg chamiga')
        messages.error(request, 'NO SE PUEDE ELIMINAR AL MIEMBRO porque es parte de un grupo') 
        return redirect('/sistema/listarMiembro')
    id_domicilio=miembroo.domicilio.id_domicilio
    domicilio=Domicilio.objects.get(id_domicilio=id_domicilio)
    id_telefono=miembroo.telefono.id_telefono
    telefono=Telefono.objects.get(id_telefono=id_telefono)
    id_tipo_telefono=telefono.tipo_telefono.id_tipo_telefono
    tipo_telefono=Tipo_Telefono.objects.get(id_tipo_telefono=id_tipo_telefono)
    domicilio.borrado=True
    miembroo.borrado=True
    telefono.borrado=True
    tipo_telefono.borrado=True
    domicilio.save()
    miembroo.save()
    telefono.save()
    tipo_telefono.save()
    return redirect('/sistema/listarMiembro')

def validarMiembro(request):
    dni = request.GET.get('dni')
    data = {
        'is_taken': Miembro.objects.filter(dni=dni).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Este miembro ya existe'
    print(data)
    return JsonResponse(data)

def crearTipo_Reunion(request):
    if request.method == 'POST':
        tipo_reunion_form= Tipo_ReunionForm(request.POST)
        if tipo_reunion_form.is_valid():
            tipo_reunion_form.save()
            return redirect('/sistema/listarTipo_Reunion')
    else:
        tipo_reunion_form=Tipo_ReunionForm()
    return render(request,'sistema/crearTipo_Reunion.html',{'tipo_reunion_form':tipo_reunion_form})

def editarTipo_Reunion(request,id_tipo_reunion):
    tipo_reunion=Tipo_Reunion.objects.get(id_tipo_reunion=id_tipo_reunion)
    if request.method == 'GET':
        tipo_reunion_form = Tipo_ReunionForm(instance = tipo_reunion)
    else:
        tipo_reunion_form=Tipo_ReunionForm(request.POST,instance=tipo_reunion)
        if tipo_reunion_form.is_valid():
            tipo_reunion_form.save()
        return redirect('/sistema/listarTipo_Reunion')
    return render(request,'sistema/crearTipo_Reunion.html',{'tipo_reunion_form':tipo_reunion_form})

def listarTipo_Reunion(request):
    tipo_reuniones = Tipo_Reunion.objects.filter(borrado=False)
    return render(request,'sistema/listarTipo_Reunion.html',{'tipo_reuniones':tipo_reuniones})

def eliminarTipo_Reunion(request,id_tipo_reunion):
    tipo_reunion=Tipo_Reunion.objects.get(id_tipo_reunion=id_tipo_reunion)
    if Reunion.objects.filter(tipo_reunion=tipo_reunion ).exists():
        messages.error(request, 'NO SE PUEDE ELIMINAR AL tipo de reunion porque hay una reunion de este tipo activa') 
        return redirect('/sistema/listarTipo_Reunion')    
    else:
        tipo_reunion.borrado=False
        tipo_reunion.save()
    return redirect('/sistema/listarTipo_Reunion/')

def crearReunion(request):
    if request.method == 'POST':
        reunion_form=ReunionForm(request.POST)
        domicilio_form=DomicilioForm(request.POST)
        if reunion_form.is_valid()and domicilio_form.is_valid():
            print('entre capa')
            reunion=reunion_form.save(commit=False)
            domicilio=domicilio_form.save(commit=False)
            reunion.domicilio=domicilio
            domicilio.save()
            reunion.save()
            return redirect('/sistema/listarReunion')
    else:
        reunion_form=ReunionForm()
        domicilio_form=DomicilioForm()
    return render(request,'sistema/crearReunion.html',{'reunion_form':reunion_form,'domicilio_form':domicilio_form})

def editarReunion(request,id_reunion):
    reunion = Reunion.objects.get(id_reunion=id_reunion)
    domicilio=Domicilio.objects.get(id = reunion.domicilio.id)
    if request.method == 'GET':
        reunion_form=ReunionForm(instance = reunion)
        domicilio_form=DomicilioForm(intance = domicilio)
    else:
        reunion_form=ReunionForm(request.POST,instance=reunion)
        domicilio_form=DomicilioForm(instance = domicilio)
        if reunion_form.is_valid() and domicilio_form.is_valid():
            print('entre capa')
            reunion=reunion_form.save(commit=False)
            domicilio=domicilio_form.save(commit=False)
            reunion.domicilio=domicilio
            domicilio.save()
            reunion.save()
        return redirect('/sistema/listarReunion')
    return render(request,'sistema/crearReunion.html',{'reunion_form':reunion_form,'domicilio_form':domicilio_form})

def listarReunion(request):
    reuniones = Reunion.objects.filter(borrado=False)
    return render(request,'sistema/listarReunion.html',{'reuniones':reuniones})      

def eliminarReunion(request,id_reunion):
    reunion=Reunion.objects.get(id_reunion=id_reunion)
    domicilio=Domicilio.objects.get(id_domicilio=reunion.domicilio.id_domicilio)
    reunion.borrado=True
    domicilio.borrado=True
    reunion.save()
    domicilio.save()
    return redirect('/sistema/listarReunion/')

def agregarAsistencia(request):
    if request.method == 'POST':
        asistencia_form=AsistenciaForm(request.POST)
        if asistencia_form.is_valid():
            asistencia_form.save()
            return redirect('home')
    else:
        asistencia_form=AsistenciaForm()
    return render(request,'sistema/agregarAsistencia.html',{'asistencia_form':asistencia_form})

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
    return render(request,'sistema/agregarRespuesta.html',{'respuesta_form':respuesta_form})