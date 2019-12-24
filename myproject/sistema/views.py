from django.shortcuts import render,redirect
from .forms import MiembroForm,Tipo_ReunionForm,ReunionForm,AsistenciaForm,Horario_DisponibleForm,Tipo_TelefonoForm
from .forms import TelefonoForm,EncuestaForm,PreguntaForm,RespuestaForm,GrupoForm,DomicilioForm,ConfiguracionForm
from .forms import LocalidadForm,ProvinciaForm,BarrioForm,Estado_CivilForm,Telefono_ContactoForm
from .models import Miembro,Grupo,Tipo_Reunion,Reunion,Tipo_Telefono,Telefono,Domicilio,Horario_Disponible
from .models import Provincia, Localidad, Barrio,Estado_Civil,Telefono_Contacto,Asistencia,Configuracion
from datetime import date
import datetime
from django.contrib import messages
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .serializers import ProvinciaSerializer,LocalidadSerializer,BarrioSerializer,AsistenciaSerializer, GrupoSerializer, MiembroSerializer
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@login_required
def Home(request):
    usuario = request.user
    context ={'usuario':usuario}
    return render(request,'sistema/index.html',context)

def auditoriaMiembro(request):
    auditoria_miembro = Miembro.history.all()
    context = {'auditoria_miembro': auditoria_miembro}
    return render(request, 'sistema/auditoriaMiembro.html', context)

def auditoriaReunion(request):
    auditoria_reunion = Reunion.history.all()
    context = {'auditoria_reunion': auditoria_reunion}
    return render(request, 'sistema/auditoriaReunion.html', context)

def configuracion(request):
    if request.method == 'POST':
        configuracion_form = ConfiguracionForm(request.POST)
        print(configuracion_form)
        if configuracion_form.is_valid():
            configuracion_form.save()
            return redirect('home')
    else:
        configuracion_form = ConfiguracionForm()
    return render(request,'sistema/configuracion.html',{'configuracion_form':configuracion_form})

def crearGrupo(request):
    miembros=Miembro.objects.all()
    if request.method == 'POST':
        grupo_form = GrupoForm(request.POST)
        print(grupo_form.errors.as_data())
        print(request.POST)
        if grupo_form.is_valid():
            grupo_form.save()
            return redirect('/sistema/listarGrupo')
    else:
        grupo_form=GrupoForm()
    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form,'miembros':miembros})

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
    configuracion_form = Configuracion.objects.all().last()
    return render(request,'sistema/listarMiembro.html',{'miembros':miembros,'configuracion_form':configuracion_form})

def crearMiembro(request):
    provincia_form=Provincia.objects.all()
    if request.method == 'POST':
        
        miembro_form=MiembroForm(request.POST)
        miembro=miembro_form.save(commit=False)
        miembro.changeReason ='Creacion'

        barrio_form=request.POST.get('barrio')
        print(barrio_form)
        barrio=Barrio.objects.get(id_barrio=barrio_form)

        estado_civil_form=request.POST.get('estado_civil')
        estado_civil=Estado_Civil.objects.get(id_estado=estado_civil_form)

        domicilio_form=DomicilioForm(request.POST)
        domicilio=domicilio_form.save(commit=False)
        domicilio.barrio=barrio
        domicilio.save()


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
            messages.error(request, 'fecha de nacimiento incorrecta')
            barrio = Barrio.objects.all()
            localidad_form=Localidad.objects.all()
            provincia_form=Provincia.objects.all()
            estado_civil_form=request.POST.get('estado_civil')
            return render(request,'sistema/editarMiembro.html',{'provincia_form':provincia_form,'localidad_form':localidad_form,'barrio':barrio,'estado_civil_form':estado_civil_form,'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})
        else:
            miembro.domicilio=domicilio
            miembro.estado_civil=estado_civil
            miembro.horario_disponible=horario
            if  telefono != None:
                miembro.telefono=telefono
            miembro.nombre=miembro.nombre.capitalize()
            miembro.apellido=miembro.apellido.upper()
            miembro.borrado=False
            miembro_contacto=request.POST.get('miembro')
            if miembro_contacto != None:
                print(miembro_contacto)
                miembro_cont=Miembro.objects.get(dni=miembro_contacto)
                tel_contacto=Telefono_Contacto()
                tel_contacto.miembro=miembro_cont
                tel_contacto.save()
            miembro.save()

            return redirect('/sistema/listarMiembro')
        
    else:
        provincia_form=Provincia.objects.all()
        localidad_form=Localidad.objects.all()
        barrio_form=Barrio.objects.all()
        domicilio_form=DomicilioForm()
        estado_civil_form=Estado_Civil.objects.all()
        miembro_form=MiembroForm()
        tipo_telefono_form=Tipo_TelefonoForm()
        telefono_form=TelefonoForm()
        horario_form=Horario_DisponibleForm()
        telefono_contacto_form=Miembro.objects.all()
        return render(request,'sistema/crearMiembro.html',{'telefono_contacto_form':telefono_contacto_form,'estado_civil_form':estado_civil_form,'provincia_form':provincia_form,'localidad_form':localidad_form,'barrio_form':barrio_form,'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})

def editarMiembro(request,dni):
    miembro = Miembro.objects.get(dni= dni)
    estado_civil_form = Estado_Civil.objects.all()
    id_domicilio=miembro.domicilio.id_domicilio
    domicilio=Domicilio.objects.get(id_domicilio=id_domicilio)
    barrio = Barrio.objects.all()
    localidad_form=Localidad.objects.all()
    provincia_form=Provincia.objects.all()
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
        barrio_form=BarrioForm()
    
    else:
        miembro_form=MiembroForm(request.POST,instance=miembro)
        domicilio_form=DomicilioForm(request.POST,instance=domicilio)
        horario_form=Horario_DisponibleForm(request.POST,instance=horario_disponible)
        telefono_form=TelefonoForm(request.POST,instance=telefono)
        tipo_telefono_form=Tipo_TelefonoForm(request.POST,instance=tipo_telefono)
        estado_civil_form=request.POST.get('estado_civil')
        print(estado_civil_form)
        estado=Estado_Civil.objects.get(id_estado=estado_civil_form)
        barrio_form = request.POST.get('barrio')
        barrio=Barrio.objects.get(barrio=barrio_form)
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

                miembro.estado_civil=estado

                domicilio=domicilio_form.save(commit=False)
                domicilio.barrio = barrio
                domicilio.save()

                horario=horario_form.save()
                
                miembro.nombre=miembro.nombre.capitalize()
                miembro.apellido=miembro.apellido.upper()
                miembro.changeReason ='Modificacion'
                miembro.save()

                return redirect('/sistema/listarMiembro')
                     
        

    return render(request,'sistema/editarMiembro.html',{'provincia_form':provincia_form,'localidad_form':localidad_form,'barrio':barrio,'estado_civil_form':estado_civil_form,'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})

def eliminarMiembro(request,dni):
    miembroo = Miembro.objects.get(dni=dni)
    if Grupo.objects.filter(miembro = miembroo,borrado=False).exists():
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
    miembroo.changeReason ='Eliminacion'
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
        nombrecito=request.POST.get('nombre')
        if tipo_reunion_form.is_valid():
            if Tipo_Reunion.objects.filter(nombre=nombrecito):
                messages.error(request,'Nombre repetido')
            else:
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

        nombrecito=request.POST.get('nombre')
        reunion_form=ReunionForm(request.POST)
        barrio_form=request.POST.get('barrio')
        barrio=Barrio.objects.get(barrio=barrio_form)
        domicilio_form=DomicilioForm(request.POST)

        horario_form= Horario_DisponibleForm(request.POST)
        horario=horario_form.save()
        print('-0-')
        print(horario)

        if reunion_form.is_valid()and domicilio_form.is_valid():
            if Reunion.objects.filter(nombre=nombrecito).exists():
                messages.error(request, 'Nombre no disponible')
            else:
                reunion=reunion_form.save(commit=False)
                domicilio=domicilio_form.save(commit=False)
                domicilio.barrio=barrio
                print(domicilio)
                domicilio.save()
                reunion.changeReason ='Creacion'
                reunion.domicilio=domicilio
                reunion.horario=horario
                reunion.save()
                return redirect('/sistema/listarReunion')
    else:
        provincia_form=Provincia.objects.all().order_by('provincia')
        localidad_form=Localidad.objects.all()
        barrio_form=Barrio.objects.all()
        reunion_form=ReunionForm()
        domicilio_form=DomicilioForm()
        horario_form=Horario_DisponibleForm()
    return render(request,'sistema/crearReunion.html',{'horario_form':horario_form,'barrio_form':barrio_form,'localidad_form':localidad_form,'provincia_form':provincia_form,'reunion_form':reunion_form,'domicilio_form':domicilio_form})

def editarReunion(request,id_reunion):
    reunion = Reunion.objects.get(id_reunion=id_reunion)
    id = reunion.domicilio.id_domicilio
    domicilio=Domicilio.objects.get(id_domicilio = id)
    idd= reunion.horario.id_horario_disponible
    horario=Horario_Disponible.objects.get(id_horario_disponible=idd)
    provincia_form=Provincia.objects.all().order_by('provincia')
    localidad_form=Localidad.objects.all()
    barrio_form=Barrio.objects.all()
    if request.method == 'GET':
        reunion_form=ReunionForm(instance = reunion)
        domicilio_form=DomicilioForm(instance = domicilio)
        horario_form = Horario_DisponibleForm(instance=horario)
        
    else:
        nombrecito=request.POST.get('nombre')
        reunion_form=ReunionForm(request.POST,instance=reunion)
        horario_form=Horario_DisponibleForm(request.POST,instance=horario)
        domicilio_form=DomicilioForm(instance = domicilio)
        domicilio=domicilio_form.save(commit=False)
        print(reunion_form.errors.as_data())
        if reunion_form.is_valid():
            reunion=reunion_form.save(commit=False)
            reunion.domicilio=domicilio
            domicilio.save()
            reunion.changeReason ='Modificacion'
            reunion.save()
            return redirect('/sistema/listarReunion')
    return render(request,'sistema/editarReunion.html',{'barrio_form':barrio_form,'localidad_form':localidad_form,'provincia_form':provincia_form,'horario_form':horario_form,'reunion_form':reunion_form,'domicilio_form':domicilio_form})

def listarReunion(request):
    reuniones = Reunion.objects.filter(borrado=False)
    configuracion_form = Configuracion.objects.all().last()
    return render(request,'sistema/listarReunion.html',{'reuniones':reuniones,'configuracion_form':configuracion_form})      

def eliminarReunion(request,id_reunion):
    reunion=Reunion.objects.get(id_reunion=id_reunion)
    domicilio=Domicilio.objects.get(id_domicilio=reunion.domicilio.id_domicilio)
    reunion.borrado=True
    domicilio.borrado=True
    reunion.changeReason ='Eliminacion'
    reunion.save()
    domicilio.save()
    return redirect('/sistema/listarReunion/')

def agregarAsistencia(request):
    if request.method == 'POST':
        reunion_form = request.POST.get('reunion')
        reunion=Reunion.objects.get(id_reunion=reunion_form)
        grupo= reunion.grupo
        miembros = Miembro.objects.filter(grupo=grupo)
        print('--------------------')
        print(miembros)
        fecha = request.POST.get('fecha')
        print('--------1--------')
        for miembro in miembros:
            asistencia=Asistencia()
            asistencia.miembro=miembro
            asistencia.fecha=fecha
            asistencia.reunion=reunion
            asistencia.presente=False
            asistencia.save()
        for check in request.POST.getlist('check[]'):
            miembro=Miembro.objects.get(dni=check)
            asistencia = Asistencia.objects.get(miembro_id = check,fecha=fecha)
            asistencia.presente=True
            asistencia.save()
            print(check)
        return redirect('home')
    else:
        asistencia_form=AsistenciaForm()
        reunion_form=Reunion.objects.all()
        miembro_form=Miembro.objects.all()
    return render(request,'sistema/agregarAsistencia.html',{'miembro_form':miembro_form,'asistencia_form':asistencia_form,'reunion_form':reunion_form})

def verAsistencia(request):
    if request.method == 'POST':
        print('wenas')
    else:
        reunion=Reunion.objects.all()
        asistencia = Asistencia.objects.all()
    return render(request,'sistema/verAsistencia.html',{'asistencia':asistencia})


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

@csrf_exempt
def provinciasList(request):
    """
    List all code serie, or create a new serie.
    """
    if request.method == 'GET':
        provincia = Provincia.objects.all()
        serializer = ProvinciaSerializer(provincia, many=True)
        result = dict()
        result = serializer.data
        return JSONResponse(result)

@csrf_exempt
def localidadesList(request):
    """
    List all code serie, or create a new serie.
    """
    pv=request.GET.get('provincia',None)
    prov=Provincia.objects.get(provincia=pv)
    if request.method == 'GET':
        localidad = Localidad.objects.filter(provincia=prov).order_by('localidad')
        serializer = LocalidadSerializer(localidad, many=True)
        result = dict()
        result = serializer.data
        return JSONResponse(result)

@csrf_exempt
def barriosList(request):
    lc=request.GET.get('localidad',None)
    print(request.GET)
    localidad=Localidad.objects.get(id_localidad=lc)
    if request.method == 'GET':
        barrio = Barrio.objects.filter(localidad=localidad).order_by('barrio')
        serializer = BarrioSerializer(barrio, many=True)
        result = dict()
        result = serializer.data
        return JSONResponse(result)

@csrf_exempt
def GrupoTable(request):
    print(request.GET)
    reunion= request.GET.get('grupo',None)
    rn = Reunion.objects.get(id_reunion=reunion)
    gr= rn.grupo
    if request.method == 'GET':
        grupos = Grupo.objects.prefetch_related('miembro').filter(id_grupo=gr.id_grupo)
        serializer = GrupoSerializer(grupos, many=True)
        result = dict()
        result = serializer.data
        #print("No ta")
        return JSONResponse(result)

@csrf_exempt
def MiembroTable(request):
    print('0')
    if request.method == 'GET':
        miembros=Miembro.objects.prefetch_related('grupo_set')
        serializer = MiembroSerializer(miembros, many=True)
        result = dict()
        result = serializer.data
        #print("No ta")
        return JSONResponse(result)

@csrf_exempt
def AsistenciaTable(request):
    print('0')
    if request.method == 'GET':
        print('1')
        reunion = request.GET.get('miembros',None)
        rn=Reunion.objects.get(id_reunion=reunion)
        print(rn)
        print('2')
        grupo=rn.grupo
        miembros= grupo.miembro
        mb= Grupo.objects.prefetch_related('miembro').filter(id_grupo=grupo.id_grupo)
        print(mb)
        print('3')
        asistencia= Asistencia.objects.all()
        serializer = AsistenciaSerializer(asistencia, many=True)
        result = dict()
        result = serializer.data
        #print("No ta")
        return JSONResponse(result)

@csrf_exempt
def sexoList(request):
    sx = request.GET.get('mb',None)
    print(sx)
    print('0')
    if request.method == 'GET':
        miembros = None
        if sx == 'Femenino':
           miembros= Miembro.objects.filter(sexo='Femenino')
        if sx == 'Masculino':
            miembros = Miembro.objects.filter(sexo = 'Masculino')
        if sx == 'Ambos': 
            miembros = Miembro.objects.all()
        print(miembros)
        serializer = MiembroSerializer(miembros, many=True)
        result = dict()
        result = serializer.data
        #print("No ta")
        return JSONResponse(result)
    
