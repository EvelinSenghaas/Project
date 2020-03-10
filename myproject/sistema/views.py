from django.shortcuts import render,redirect
from .forms import *
from .models import *
from mensajeria.models import *
from mensajeria.views import *
from datetime import date
import datetime
from usuario.models import *
from django.db.models import Avg
from django.db.models import Count
from django.db import models
from django.db.models import Max
from django.contrib import messages
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .serializers import *
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import random
from usuario.forms import CustomUserCreationForm
from django.contrib.auth import login as dj_login, logout, authenticate
import base64

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def permiso(request, p):
    permisos = request.user.rol.permisos.all()
    for permiso in permisos:
        if p == permiso.id_permiso:
            return True
    return False

def days_between(d1, d2):
    return abs(d2 - d1).days

def color():
    random_number = random.randint(0,16777215)
    hex_number = str(hex(random_number))
    hex_number ='#'+ hex_number[2:]
    return hex_number

def aviso(fecha,rn):
    #weno la idea aca es ver cuantas faltas tiene el vago y depende de eso emito el aviso 
    #1. traigo las inasistencias
    reunion=Reunion.objects.get(id_reunion=rn)
    enc = reunion.grupo.encargado
    usr=CustomUser.objects.get(id=enc)
    if Asistencia.objects.filter(miembro_id=usr.miembro.dni,reunion_id=rn,fecha=fecha).exists():
        reg = Asistencia.objects.get(miembro_id=usr.miembro.dni,reunion_id=rn,fecha=fecha)
        if reg.presente == False:
            cant=0
            tp= Tipo_Encuesta.objects.get(id_tipo_encuesta=4)
            n=tp.cantidad
            n-=1#el de hoy ya es 1 por eso resto
            cant+=1
            #bueno hoy falto, ahora tengo que ver si las n reuniones pasadas falto tmb
            registros = Asistencia.objects.filter(miembro_id=usr.miembro.dni,reunion_id=rn,fecha__lte=fecha)[:n]
            for registro in registros:
                if registro.presente == False:
                    cant+=1
            if cant >= n:
                mensaje="Hola! se ah detectado que el miembro " + usr.miembro.apellido + ", " + usr.miembro.nombre + " falto " + str(cant) + " o mas veces de seguido a la reunion " + reunion.nombre + ", "
                miembros=[] #tengo que poner aca los admin
                enviarWhatsapp(mensaje,miembros)

@login_required
def Home(request):
    #Tengo que ver de recuperar el ultimo registro de asistencia por reunion, si pasaron mas de 7 dias 
    #y no hubo un registro, ponerle falta al encargado
    usuario = request.user
    miembro = Miembro.objects.get(dni=usuario.miembro_id)
    if miembro.sexo=="Femenino":
        sexo="Femenino"
    else:
        sexo="Masculino"
    context ={'usuario':usuario,'sexo':sexo}
    
    #tengo que ver si el usr tiene una falta que no ingreso para eso
    #obtengo todas sus reuniones
    tipo= Tipo_Encuesta.objects.get(id_tipo_encuesta=3)
    cant=tipo.cantidad #obtendo la cantidad de faltas consecutivas actuales admisibles
    reuniones=Reunion.objects.filter(grupo__encargado=request.user.id)
    for reunion in reuniones: #ahora por cada reunion comparo las fechas de los ultimos registros con hoy
        if Asistencia.objects.filter(reunion=reunion.id_reunion).exists():
            asistencia=Asistencia.objects.filter(reunion=reunion.id_reunion).last()
            fecha_rn=asistencia.fecha
            hoy=date.today()
            print(days_between(hoy, fecha_rn))
            dias=days_between(hoy, fecha_rn)
            if dias > 7: #si paso una semana y no se puso asistencia a la reunion entonces.... miembro lo defini bien arriba para ver su genero
                ast=Asistencia(miembro=miembro,presente=False,justificado=False,reunion=reunion,fecha=hoy)
                ast.save()
                #pongo la falta y veo cuantas anteriores tiene para notificar
                aviso(hoy,reunion.id_reunion)
        #ahora que le puse la falta es el momento de contar cuantas faltas CONSECUTIVAS TIENE
        consulta=Asistencia.objects.filter(miembro=miembro,justificado=False,reunion=reunion.id_reunion).order_by('fecha')[:cant]
        cantidad = len (list(consulta)) #paso la cantidad de registros de faltas que encontro a cantidad
        if cantidad >= cant: #si la cantidad es >= al numero admisible de consecutivas entonces le creo una encuesta pendiente
            encuesta= Encuesta()
            encuesta.tipo=tipo
            encuesta.miembro=miembro
            encuesta.fecha_envio=date.today()
            encuesta.respondio=False
            encuesta.reunion=reunion
            encuesta.save()
            return redirect('/sistema/agregarRespuesta')

    if Asistencia.objects.filter(miembro=miembro,justificado=False).exists():
        #tiene que haber un counter lo necesito para elegir el tipo xd
        #aca tengo que contar cuantas faltas tiene por ahora es cada 1 y poner la reunion jiji
        faltas=Asistencia.objects.filter(miembro=miembro,justificado=False)
        for falta in faltas:
            if not(Encuesta.objects.filter(tipo_id=1,miembro_id=miembro.dni,fecha_envio=falta.fecha,reunion=falta.reunion).exists()):
                encuesta= Encuesta()
                encuesta.borrado=False #ver si realmente puedo borrar una encuesta xd creeria que no se debe
                encuesta.tipo=Tipo_Encuesta.objects.get(id_tipo_encuesta=1)
                encuesta.miembro=miembro
                encuesta.respondio=False
                encuesta.fecha_envio = falta.fecha
                encuesta.reunion=falta.reunion
                encuesta.save() #Esto quiere decir que tenia una falta no mas
                mensaje= "Hola "+miembro.nombre+"! tienes una encuesta pendiente por la falta en la reunion "+falta.reunion.nombre+" el dia "+ str(falta.fecha) +" por favor ingresa al sistema y dirigete a 'encuestas pendientes'"
                miembros=[] #porque no le voy a mandar realmente jiji
                enviarWhatsapp(mensaje,miembros)
                asunto = "Encuesta Pendiente"
                enviarMail(miembros,asunto,mensaje)

    #Bueno esto no es lo mejor pero la idea es ver cuando fue la ultima vez que envie la encuesta tipo 2 osea estado de las reuniones
    #Para eso obtengo el ultimo registro de encuesta.tipo==2 veo cuantos dias pasaron y si pasa a la cantidad especificada
    #pum envio encuestas para todos!!! yupi
    if Encuesta.objects.filter(tipo_id=2).exists():
        encuesta=Encuesta.objects.filter(tipo_id=2).last()
        fecha=encuesta.fecha_envio
        hoy=date.today()
        print(days_between(hoy, fecha))
        dias=days_between(hoy, fecha)
        tipo= Tipo_Encuesta.objects.get(id_tipo_encuesta=2)
        cant=tipo.cantidad
        if dias >= cant:
            print("tamos fritos xd") 
            #aca llamo a otra vista ni no vimo
            #A cada miembro en las reuniones tendria que mandarle una encuesta a su wss, osea el link
            #Pero deberia crear una encuesta por miembro?? o simplemente le envio el link y si respondo cuento cuantos respondieron
            #eso me parece las obvio, entonces le mando el enlace y a medida que van entrando le creo
            #localhost:8000/sistema/agregarRespuesta/reunion=1 y pum envio
    
    return render(request,'sistema/index.html',context)

@login_required
def estadistica_miembro(request):
    if permiso(request, 43):
        usuarios = CustomUser.objects.all()
        return render(request,'sistema/estadistica_miembro.html',{'usuarios':usuarios})
    else:
        return redirect('home')

@login_required
def estadistica_reunion(request):
    if permiso(request, 43):
        if permiso(request, 10):
            reuniones=Reunion.objects.all()
        else:
            reuniones=Reunion.objects.filter(grupo__encargado=request.user.id)
        #reuniones = Reunion.objects.all()
        return render(request,'sistema/estadistica_reunion.html',{'reuniones':reuniones})
    else:
        return redirect('home')

@login_required
def estadistica_asistencias(request):
    if permiso(request, 43):
        if permiso(request, 10):
            reuniones=Reunion.objects.all()
        else:
            reuniones=Reunion.objects.filter(grupo__encargado=request.user.id)
        #reuniones = Reunion.objects.all()
        miembros = Miembro.objects.all()
        roles = Rol.objects.filter(borrado=False)
        return render(request,'sistema/estadistica_asistencias.html',{'reuniones':reuniones,'miembros':miembros,'roles':roles})
    else:
        return redirect('home')

@login_required
def auditoriaMiembro(request):
    if permiso(request, 42):
        auditoria_miembro = Miembro.history.all()
        configuracion_form = Configuracion.objects.all().last()
        context = {'auditoria_miembro': auditoria_miembro,'configuracion_form':configuracion_form}
        return render(request, 'sistema/auditoriaMiembro.html', context)
    else:
        return redirect('home')

@login_required
def auditoriaReunion(request):
    if permiso(request, 42):
        auditoria_reunion = Reunion.history.all()
        configuracion_form = Configuracion.objects.all().last()
        context = {'auditoria_reunion': auditoria_reunion,'configuracion_form':configuracion_form}
        return render(request, 'sistema/auditoriaReunion.html', context)
    else:
        return redirect('home')

@login_required
def auditoriaAsistencia(request):
    if permiso(request, 42):
        auditoria_asistencia = Asistencia.history.all()
        configuracion_form = Configuracion.objects.all().last()
        context = {'auditoria_asistencia': auditoria_asistencia,'configuracion_form':configuracion_form}
        return render(request, 'sistema/auditoriaAsistencia.html', context)
    else:
        return redirect('home')

@login_required
def configuracion(request):
    if permiso(request, 24):
        conf=Configuracion.objects.all()
        if conf:
            conf=conf[0]
            configuracion_form = ConfiguracionForm(instance=conf)
        else:
            configuracion_form = ConfiguracionForm()
            
        if request.method == 'POST':
            configuracion_form = ConfiguracionForm(request.POST,instance=conf)
            print(configuracion_form)
            if configuracion_form.is_valid():
                dato = configuracion_form.save(commit=False)
                dato.logo=request.FILES['logo'].file.read()
                dato.save()
                return redirect('home')
        
        return render(request,'sistema/configuracion.html',{'configuracion_form':configuracion_form})
    else:
        return redirect('home')

def obtenerLogo(request):
    data={}
    dato = list(Configuracion.objects.all())[0]
    binary = base64.b64encode(dato.logo)
    cadena = str(binary)
    cadena = cadena[2:]
    total = len(cadena)
    logo = cadena[:total - 1]
    logo = "data:image/png;base64," + logo
    data = {
        'logo': logo,
    }
    
    
    return JsonResponse(data)

@login_required
def crearGrupo(request):
    if permiso(request, 14):
        miembros=Miembro.objects.all()
        usuarios=CustomUser.objects.filter(is_active=True)
        if request.method == 'POST':
            try:
                grupo_form = GrupoForm(request.POST)
                grupo=grupo_form.save(commit=False)
                capacidad = grupo.capacidad
                if capacidad < len(request.POST.get('miembro')):
                    messages.error(request, 'La cantidad de miembros excede la capacidad maxima del grupo')
                    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form, 'usuarios':usuarios})
                    
                grupo.encargado=request.POST.get('encargado')
                grupo.changeReason ='Creacion'
                grupo.save()
                
                encargado = CustomUser.objects.get(id=grupo.encargado)
                miembros=request.POST.getlist('miembro')
                miembros.append(encargado.miembro)
                try:
                    grupo.miembro.set(miembros)
                except:
                    grupo.miembro.set(request.POST.getlist('miembro'))
                grupo.save()
            except:
                print('algo salio mal')
            if permiso(request, 17) or permiso(request, 18):
                return redirect('/sistema/listarGrupo')
            else:
                return redirect('home')
        else:
            grupo_form=GrupoForm()
        return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form,'miembros':miembros,'usuarios':usuarios})
    else:
        return redirect('home')

@login_required
def listarGrupo(request):
    if permiso(request, 17):
        grupos = Grupo.objects.filter(borrado=False, encargado= request.user.id)
    if permiso(request, 18):
        grupos = Grupo.objects.filter(borrado=False)
    if not(permiso(request, 18) or permiso(request, 17)):
        return redirect('home')
    #bien ahora la idea es ponerle el nombre y apellido del encargado en grupo.encargado, vemos
    for grupo in grupos:
        enc = grupo.encargado
        enc = CustomUser.objects.get(id=enc)
        encargado = Miembro.objects.get(dni = enc.miembro_id)
        grupo.encargado = encargado.apellido + ", " + encargado.nombre
    configuracion_form = Configuracion.objects.all().last()
    return render(request,'sistema/listarGrupo.html',{'grupos':grupos,'configuracion_form':configuracion_form})

@login_required
def validarGrupo(request):
    nombre = request.GET.get('nombre')
    data = {
        'is_taken': Grupo.objects.filter(nombre=nombre,borrado = False).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Este nombre de grupo ya existe, por favor elige otro nombre'
    print(data)
    return JsonResponse(data)

@login_required
def editarGrupo(request,id_grupo):
    if permiso(request, 16):
        usuarios= CustomUser.objects.filter(is_active=True)
        grupo = Grupo.objects.get(id_grupo=id_grupo)
        encargado = grupo.encargado
        miembros = grupo.miembro.all()
        #bien tengo que ver todos los miembros que estan en ese rango etario
        desde = grupo.desde
        hasta = grupo.hasta
        sx = grupo.sexo
        hoy = date.today()
        #el hasta es mas chico que el desde, por lo tanto para filtrar un fecha de nac tiene que estar entre
        # fecha__range(f_min,f_max)
        #donde f_min = al hasta anho 2000 y la f_max va a ser 2005 seria el desde
        dif = hoy.year - int(hasta)
        f_min = date(int(dif),12,31)
        dif = hoy.year - int(desde)
        f_max = date(int(dif),12,31)
        if sx != 'Ambos':
            todos=Miembro.objects.filter(sexo = sx, fecha_nacimiento__range=(f_min,f_max))
        else:
            todos=Miembro.objects.filter(fecha_nacimiento__range=(f_min,f_max))
        if request.method =='GET':
            grupo_form=GrupoForm(instance=grupo)
        else:
            grupo_form=GrupoForm(request.POST,instance=grupo)
            if grupo_form.is_valid():
                grupo=grupo_form.save(commit=False)
                capacidad = grupo.capacidad
                if capacidad < len(request.POST.get('miembro')):
                    messages.error(request, 'La cantidad de miembros excede la capacidad maxima del grupo')
                    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form, 'usuarios':usuarios})
                grupo.miembro.set(request.POST.getlist('miembro'))
                grupo.changeReason='Modificacion'
                grupo.save()
            if permiso(request, 17) or permiso(request, 18):
                return redirect('/sistema/listarGrupo')
            else:
                return redirect('home')
        return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form,'encargado':encargado,'todos':todos,'miembros':miembros,'usuarios':usuarios})
    else:
        return redirect('home')

@login_required
def eliminarGrupo(request,id_grupo):
    if permiso(request, 15):
        grupo = Grupo.objects.get(id_grupo=id_grupo)
        grupo.borrado=True
        grupo.changeReason='Eliminacion'
        grupo.save()
        if permiso(request, 17) or permiso(request, 18):
            return redirect('/sistema/listarGrupo')
        else:
            return redirect('home')
    else:
        return redirect('home')

@login_required
def listarMiembro(request):
    if permiso(request, 4): #tiene permiso para ver sus miembros
        miembros=[]
        grupos = Grupo.objects.filter(encargado = request.user.id)
        for grupo in grupos:
            mbs = grupo.miembro.all()
            for mb in mbs:
                if not(mb in miembros) and (request.user.miembro.dni !=mb.dni):
                    miembros.append(mb)

    if permiso(request, 5): #tiene permiso para ver todos los miembros
        miembros = Miembro.objects.filter(borrado=False).exclude(dni=request.user.miembro.dni)
    
    if not(permiso(request, 5) or permiso(request, 4)):
        return redirect('home')
    for miembro in miembros:        
        miembro.fecha_nacimiento = miembro.edad(miembro.fecha_nacimiento)
    configuracion_form = Configuracion.objects.all().last()
    return render(request,'sistema/listarMiembro.html',{'miembros':miembros,'configuracion_form':configuracion_form})

@login_required
def crearMiembro(request):
    if permiso(request, 1):
        provincia_form=Provincia.objects.all()
        if request.method == 'POST':
            if 'btn-add-provincia' in request.POST:
                provincia=request.POST.get('prov',None)
                provincia=provincia.capitalize()
                if Provincia.objects.filter(provincia=provincia).exists():
                    print('')#vo tenes que cambiar esto michinita
                else:
                    prv=Provincia.objects.create(provincia=provincia,borrado=False)
                    prv.save()
                return redirect('/sistema/crearMiembro')

            if 'btn-add-localidad' in request.POST:
                localidad=request.POST.get('localidad',None)
                provincia=request.POST.get('prv',None)
                prv1=Provincia.objects.filter(provincia=provincia)
                prv=Provincia.objects.get(id_provincia=prv1[0].id_provincia)
                print(prv)
                localidad=localidad.capitalize()
                if Localidad.objects.filter(localidad=localidad).exists():
                    print('nombre repetido china')
                else:
                    lcl=Localidad.objects.create(localidad=localidad,provincia=prv,borrado=False)
                    lcl.save()
                return redirect('/sistema/crearMiembro')
            
            if 'btn-add-barrio'in request.POST:
                barrio=request.POST.get('barrioo',None)
                localidad=request.POST.get('lcl',None)
                lcl1=Localidad.objects.filter(localidad=localidad)
                lcl=Localidad.objects.get(id_localidad=lcl1[0].id_localidad)
                barrio=barrio.capitalize()
                if Barrio.objects.filter(barrio=barrio).exists():
                    print('nombre repetido china')
                else:
                    br=Barrio.objects.create(barrio=barrio,localidad=lcl,borrado=False)
                    br.save()
                return redirect('/sistema/crearMiembro')
            
            if 'btn-crear-miembro' in request.POST:
                miembro_form=MiembroForm(request.POST)
                barrio_form=request.POST.get('barrio')
                estado_civil_form=Estado_Civil.objects.all()
                domicilio_form=DomicilioForm(request.POST)
                horario_form=Horario_DisponibleForm(request.POST)
                
                if not(miembro_form.is_valid() and horario_form.is_valid() and barrio_form!=None and domicilio_form.is_valid()):
                    messages.error(request, 'Debe completar todos los campos obligatorios')
                    telefono_contacto_form=Miembro.objects.all()
                    telefono_form = TelefonoForm(request.POST)
                    tipo_telefono_form = Tipo_TelefonoForm(request.POST)
                    return render(request,'sistema/crearMiembro.html',{'telefono_contacto_form':telefono_contacto_form,'estado_civil_form':estado_civil_form,'barrio_form':barrio_form,'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})

                
                miembro=miembro_form.save(commit=False)
                miembro.changeReason ='Creacion'

                barrio=Barrio.objects.get(id_barrio=barrio_form)
                
                estado_civil=Estado_Civil.objects.get(id_estado=estado_civil_form)

                domicilio=domicilio_form.save(commit=False)
                domicilio.barrio=barrio
                domicilio.save()

                horario=horario_form.save()
                
                if Tipo_TelefonoForm(request.POST)!= None:
                    tipo_telefono_form=Tipo_TelefonoForm(request.POST)
                    tipo_telefono=tipo_telefono_form.save()
                    telefono_form=TelefonoForm(request.POST)
                    telefono=telefono_form.save(commit=False)
                    telefono.tipo_telefono=tipo_telefono
                    telefono.save()
                
                
                #return render(request,'sistema/editarMiembro.html',{'provincia_form':provincia_form,'localidad_form':localidad_form,'barrio':barrio,'estado_civil_form':estado_civil_form,'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})
                miembro.domicilio=domicilio
                miembro.estado_civil=estado_civil
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
                miembro.horario_disponible.add(horario)
                miembro.save()
            if permiso(request, 4) or permiso(request, 5):
                return redirect('/sistema/listarMiembro')
            else:
                return redirect('home')
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
    else:
        return redirect('home')

@login_required
def editarMiembro(request,dni):
    if permiso(request, 3):
        miembro = Miembro.objects.get(dni= dni)
        id_domicilio=miembro.domicilio.id_domicilio
        domicilio=Domicilio.objects.get(id_domicilio=id_domicilio)
        barrio = Barrio.objects.get(id_barrio=domicilio.barrio.id_barrio)
        localidad=Localidad.objects.get(id_localidad=barrio.localidad.id_localidad)
        if miembro.telefono != None:
            id_telefono=miembro.telefono.id_telefono
            telefono=Telefono.objects.get(id_telefono=id_telefono)
            id_tipo_telefono=telefono.tipo_telefono.id_tipo_telefono
            tipo_telefono=Tipo_Telefono.objects.get(id_tipo_telefono=id_tipo_telefono)
        else: 
            telefono=None
            tipo_telefono=None

        horario=miembro.horario_disponible.all()
        horario_disponible = Horario_Disponible.objects.get(id_horario_disponible=horario[0].id_horario_disponible)

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
            barrio_form=BarrioForm(instance=barrio)
            localidad_form=LocalidadForm(instance=localidad)
        
        else:
            miembro_form=MiembroForm(request.POST,instance=miembro)
            domicilio_form=DomicilioForm(request.POST,instance=domicilio)
            horario_form=Horario_DisponibleForm(request.POST,instance=horario_disponible)
            telefono_form=TelefonoForm(request.POST,instance=telefono)
            tipo_telefono_form=Tipo_TelefonoForm(request.POST,instance=tipo_telefono)
            if miembro_form.is_valid():
                miembro=miembro_form.save(commit=False)
                if tipo_telefono_form.is_valid() and telefono_form.is_valid() and horario_form.is_valid() and miembro_form.is_valid() and domicilio_form.is_valid():
                    if request.POST.get('prefijo') and request.POST.get('numero') != None:
                        tipo=tipo_telefono_form.save()
                        telefono=telefono_form.save(commit=False)
                        telefono.tipo_telefono=tipo
                        telefono.save()
                        miembro.telefono=telefono

                    horario=horario_form.save()
                    domicilio_form.save()
                    miembro.nombre=miembro.nombre.capitalize()
                    miembro.apellido=miembro.apellido.upper()
                    miembro.changeReason ='Modificacion'
                    miembro.save()
                    if permiso(request, 4) or permiso(request, 5):
                        return redirect('/sistema/listarMiembro')
                    else:
                        return redirect('home')
        return render(request,'sistema/editarMiembro.html',{'localidad_form':localidad_form,'barrio_form':barrio_form,'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})
    else:
        return redirect('home')

@login_required
def eliminarMiembro(request,dni):
    if permiso(request, 2):
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
        if permiso(request, 4) or permiso(request, 5):
            return redirect('/sistema/listarMiembro')
        else:
            return redirect('home')

@login_required
def validarMiembro(request):
    dni = request.GET.get('dni')
    data = {
        'is_taken': Miembro.objects.filter(dni=dni,borrado = False).exists() #ojo el piojo con el sexo
    }
    if data['is_taken']:
        data['error_message'] = 'Este miembro ya existe'
    print(data)
    return JsonResponse(data)

@login_required
def crearTipo_Reunion(request):
    if permiso(request, 11):
        if request.method == 'POST':
            tipo_reunion_form= Tipo_ReunionForm(request.POST)
            nombrecito=request.POST.get('nombre')
            if tipo_reunion_form.is_valid():
                if Tipo_Reunion.objects.filter(nombre=nombrecito):
                    messages.error(request,'Nombre repetido')
                else:
                    tipo_reunion=tipo_reunion_form.save(commit=False)
                    tipo_reunion.changeReason="Creacion"
                    tipo_reunion.save()
                    if permiso(request, 40):
                        return redirect('/sistema/listarTipo_Reunion')
                    else:
                        return redirect('home')
        else:
            tipo_reunion_form=Tipo_ReunionForm()
        return render(request,'sistema/crearTipo_Reunion.html',{'tipo_reunion_form':tipo_reunion_form})
    else:
        return redirect('home')

@login_required
def editarTipo_Reunion(request,id_tipo_reunion):
    if permiso(request, 13):
        tipo_reunion=Tipo_Reunion.objects.get(id_tipo_reunion=id_tipo_reunion)
        if request.method == 'GET':
            tipo_reunion_form = Tipo_ReunionForm(instance = tipo_reunion)
        else:
            tipo_reunion_form=Tipo_ReunionForm(request.POST,instance=tipo_reunion)
            if tipo_reunion_form.is_valid():
                tipo_reunion=tipo_reunion_form.save(commit=False)
                tipo_reunion.changeReason="Modificacion"
                tipo_reunion.save()
            return redirect('/sistema/listarTipo_Reunion')
        return render(request,'sistema/crearTipo_Reunion.html',{'tipo_reunion_form':tipo_reunion_form})
    else:
        return redirect('home')

@login_required
def listarTipo_Reunion(request):
    if permiso(request, 40):
        tipo_reuniones = Tipo_Reunion.objects.filter(borrado=False)
        configuracion_form = Configuracion.objects.all().last()
        return render(request,'sistema/listarTipo_Reunion.html',{'tipo_reuniones':tipo_reuniones,'configuracion_form':configuracion_form})
    else:
        return redirect('home')

@login_required
def eliminarTipo_Reunion(request,id_tipo_reunion):
    if permiso(request, 12):
        tipo_reunion=Tipo_Reunion.objects.get(id_tipo_reunion=id_tipo_reunion)
        if Reunion.objects.filter(tipo_reunion=tipo_reunion ).exists():
            messages.error(request, 'NO SE PUEDE ELIMINAR AL tipo de reunion porque hay una reunion de este tipo activa') 
            return redirect('/sistema/listarTipo_Reunion')    
        else:
            tipo_reunion.borrado=True
            tipo_reunion.changeReason="Eliminacion"
            tipo_reunion.save()
        return redirect('/sistema/listarTipo_Reunion/')
    else:
        return redirect('home')

@login_required
def crearReunion(request):
    if permiso(request, 6):
        if request.method == 'POST':
            reunion_form=ReunionForm(request.POST)
            reunion=reunion_form.save(commit=False)
            domicilio_form=DomicilioForm(request.POST)
            horario_form= Horario_DisponibleForm(request.POST)

            if reunion_form.is_valid()and domicilio_form.is_valid():
                if Reunion.objects.filter(nombre=reunion.nombre).exists():
                    messages.error(request, 'Nombre no disponible')
                else:
                    horario=horario_form.save(commit=False)
                    horario.save()
                    domicilio=domicilio_form.save(commit=False)
                    domicilio.save()
                    reunion.changeReason ='Creacion'
                    reunion.domicilio=domicilio
                    reunion.horario=horario
                    reunion.save()
            if permiso(request, 9) or permiso(request, 10):
                return redirect('/sistema/listarReunion')
            else:
                return redirect('home')
        else:
            localidad_form=LocalidadForm()
            barrio_form=BarrioForm()
            reunion_form=ReunionForm()
            domicilio_form=DomicilioForm()
            horario_form=Horario_DisponibleForm()
        return render(request,'sistema/editarReunion.html',{'barrio_form':barrio_form,'localidad_form':localidad_form,'horario_form':horario_form,'reunion_form':reunion_form,'domicilio_form':domicilio_form})
    else:
        return redirect('home')

@login_required
def editarReunion(request,id_reunion):
    if permiso(request, 8):
        reunion = Reunion.objects.get(id_reunion=id_reunion)
        id = reunion.domicilio.id_domicilio
        domicilio=Domicilio.objects.get(id_domicilio = id)
        idd= reunion.horario.id_horario_disponible
        horario=Horario_Disponible.objects.get(id_horario_disponible=idd)
        barrio=Barrio.objects.get(id_barrio=domicilio.barrio.id_barrio)
        localidad=Localidad.objects.get(id_localidad=barrio.localidad.id_localidad)
        if request.method == 'GET':
            reunion_form=ReunionForm(instance = reunion)
            domicilio_form=DomicilioForm(instance = domicilio)
            horario_form = Horario_DisponibleForm(instance=horario)
            barrio_form= BarrioForm(instance=barrio)
            localidad_form=LocalidadForm(instance=localidad)        
        else:
            reunion_form=ReunionForm(request.POST,instance=reunion)
            horario_form=Horario_DisponibleForm(request.POST,instance=horario)
            domicilio_form=DomicilioForm(request.POST,instance = domicilio)
            print(reunion_form.errors.as_data())
            if reunion_form.is_valid() and domicilio_form.is_valid() and horario_form.is_valid():
                domicilio.save()
                horario_form.save()
                reunion.changeReason ='Modificacion'
                reunion.save()
                if permiso(request, 9) or permiso(request, 10):
                    return redirect('/sistema/listarReunion')
                else:
                    return redirect('home')
        return render(request,'sistema/editarReunion.html',{'barrio_form':barrio_form,'localidad_form':localidad_form,'horario_form':horario_form,'reunion_form':reunion_form,'domicilio_form':domicilio_form})
    else:
        return redirect('home')

@login_required
def listarReunion(request):
    if permiso(request, 9):
        reuniones = Reunion.objects.filter(borrado=False,grupo__encargado=request.user.id)
    if permiso(request, 10):
        reuniones = Reunion.objects.filter(borrado=False)
    if not(permiso(request, 10) or permiso(request, 9)):
        return redirect('home')
    configuracion_form = Configuracion.objects.all().last()
    return render(request,'sistema/listarReunion.html',{'reuniones':reuniones,'configuracion_form':configuracion_form})      

@login_required
def eliminarReunion(request,id_reunion):
    if permiso(request, 7):
        reunion=Reunion.objects.get(id_reunion=id_reunion)
        domicilio=Domicilio.objects.get(id_domicilio=reunion.domicilio.id_domicilio)
        reunion.borrado=True
        domicilio.borrado=True
        reunion.changeReason ='Eliminacion'
        reunion.save()
        domicilio.save()
        return redirect('/sistema/listarReunion/')
    else:
        return redirect('home')

@login_required
def agregarAsistencia(request):
    if permiso(request, 19):
        if request.method == 'POST':
            reunion_form = request.POST.get('reunion')
            print("-----------------------------------")
            # print('ast: ',request.POST.get('ast-encargado'))
            reunion=Reunion.objects.get(id_reunion=reunion_form)
            grupo= reunion.grupo
            fecha = request.POST.get('fecha')
            hoy = date.today()
            #Weno voy a ver si ya pusieron asistencias ese dia capa, le mando un error
            print('fecharda: ',fecha)
            if Asistencia.objects.filter(fecha=fecha,reunion=reunion).exists():
                print('ni un cargo tu if')
                messages.error(request, 'Esta Reunion ya registro sus asistencias el dia '+ fecha)
                return redirect('/sistema/agregarAsistencia')

            if request.POST.get('ast-encargado') == "True":
                if request.POST.getlist('check[]'):
                    miembros = Miembro.objects.filter(grupo=grupo)
                    for miembro in miembros:
                        asistencia=Asistencia()
                        asistencia.miembro=miembro
                        asistencia.fecha=fecha
                        asistencia.reunion=reunion
                        asistencia.presente=False
                        justificado=False
                        asistencia.changeReason="Creacion"
                        asistencia.save()
                    for check in request.POST.getlist('check[]'):
                        print('dni: ',check)
                        miembro=Miembro.objects.get(dni=check)
                        asistencia = Asistencia.objects.get(miembro_id = check,fecha=fecha,reunion=reunion)
                        asistencia.presente=True
                        justificado=True
                        asistencia.changeReason="Creacion"
                        asistencia.save()
                else:
                    messages.error(request, 'Tenes que seleccionar los miembros que asistieron')
                    return redirect('/sistema/agregarAsistencia')
            else:
                miembro=CustomUser.objects.get(id=grupo.encargado)
                miembro.faltas +=1
                miembro.save()
                miembro=miembro.miembro_id
                miembro=Miembro.objects.get(dni=miembro)
                asistencia=Asistencia()
                asistencia.miembro=miembro
                asistencia.fecha=fecha
                asistencia.reunion=reunion
                asistencia.presente=False
                asistencia.justificado=False
                asistencia.save()
            aviso(hoy,reunion.id_reunion) # mando para verificar si el encargado falto
            # except:
            #     print('')
            #     print('hay problemas serios lina')
            #     print('')
            return redirect('/sistema/verAsistencia')
        else:
            asistencia_form=AsistenciaForm()
            if permiso(request, 10):
                reunion_form=Reunion.objects.filter(borrado=False)
            else:
                reunion_form=Reunion.objects.filter(grupo__encargado=request.user.id,borrado=False)
            miembro_form=Miembro.objects.filter(borrado=False)
        return render(request,'sistema/agregarAsistencia.html',{'miembro_form':miembro_form,'asistencia_form':asistencia_form,'reunion_form':reunion_form})
    else:
        return redirect('home')

@login_required
def editarAsistencia(request,id_asistencia):
    if permiso(request, 21):
        ast = Asistencia.objects.get(id_asistencia=id_asistencia)
        asistencia = AsistenciaForm(instance=ast)
        if request.method == 'POST':
            asistio = request.POST.get('asistio')#esto es true o false
            if ast.presente != asistio:
                ast.presente = asistio
                ast.changeReason="Modificacion"
                ast.save()
            return redirect('/sistema/verAsistencia')
        
        return render(request,'sistema/editarAsistencia.html',{'ast':ast,'asistencia':asistencia})
    else:
        return redirect('home')

@login_required
def verAsistencia(request):
    if permiso(request, 22):
        asistencia=[]
        reunion = Reunion.objects.filter(grupo__encargado=request.user.id)
        for rn in reunion:
            asistencias = Asistencia.objects.filter(reunion_id = rn.id_reunion)
            for ast in asistencias:
                if not(ast in asistencia):
                    asistencia.append(ast)
    if permiso(request, 23):
        reunion=Reunion.objects.all()
        asistencia = Asistencia.objects.all()
    if not(permiso(request, 23) or permiso(request, 22)):
        return redirect('home')
    return render(request,'sistema/verAsistencia.html',{'asistencia':asistencia,'reunion':reunion})

@login_required
def agregarEncuesta(request):
    if permiso(request, 27):
        if request.method == 'POST':
            tipo=request.POST.get('tipo')
            if request.POST.get('cantidad',None)=='None':
                cantidad=request.POST.get('cantidadd')
            else:
                cantidad=request.POST.get('cantidad')
            tipo=Tipo_Encuesta.objects.get(id_tipo_encuesta=tipo)
            tipo.cantidad=cantidad
            pregunta=request.POST.get('pregunta')
            tipo.save()
            tipo.preguntas.set(request.POST.getlist('check[]'))
            #tipo.changeReason="Creacion"
            tipo.save()
            if tipo.id_tipo_encuesta== 2:
                reuniones=request.POST.getlist('reunion[]')
                for rn in reuniones:
                    reunion=Reunion.objects.get(id_reunion=int(rn))
                    grupo=reunion.grupo
                    miembross = grupo.miembro.all()
                    miembros=[]
                    for miembro in miembross:
                        miembros.append(miembro)
                        encuesta=Encuesta(borrado=False,fecha_envio=date.today(),reunion=reunion,tipo=tipo,respondio=False) #creo la encuesta
                        #a medida que voy creando le voy a ir enviando tmb
                        encuesta.save()
                        mensaje=Mensaje.objects.get(tipo_id=4)
                        asunto=mensaje.tipo
                        mensaje=mensaje.mensaje
                        enviarWhatsapp(mensaje,miembros)
                        mensaje=mensaje + ' ->  http://localhost:8000/sistema/agregarRespuestaReunion/'+str(encuesta.id_encuesta)
                        enviarMail(miembros,asunto,mensaje)
                        miembros=[]#limpio porque voy a enviar 1 por uno
            return redirect('home')
        else:
            pregunta=Pregunta.objects.filter(borrado=False)
            tipo_encuesta=Tipo_Encuesta.objects.exclude(id_tipo_encuesta=4) #el tipo 4 es utilizado para avisos
            reuniones=Reunion.objects.filter(borrado=False)
            return render(request,'sistema/agregarEncuesta.html',{'tipo_encuesta':tipo_encuesta,'pregunta':pregunta,'reuniones':reuniones})
    else:
        return redirect('home')

@login_required
def agregarPregunta(request):
    if permiso(request, 25):
        if request.method =='POST':
            pregunta = PreguntaForm(request.POST)
            print("-----------------------------")
            print(pregunta.errors)
            print("-----------------------------")
            pregunta=pregunta.save(commit=False)
            pregunta.changeReason="Creacion"        
            tipo=request.POST.get('tipo')
            print(tipo)
            print("-----------------------------")
            pregunta.save()
            puntos=request.POST.getlist('puntos')
            print(puntos)
            print("-----------------------------")
            i=0
            if tipo=='2':
                radios=request.POST.getlist('radiosList')
                print(radios)
                for radio in radios:
                    punto=puntos[i]
                    print("--------------pto abajito---------------")
                    print(punto)
                    i+=1
                    opcion=Opciones(pregunta=pregunta, opcion=radio, puntaje=punto)
                    opcion.save()
            if tipo=='3':
                checks=request.POST.getlist('check[]')
                print(checks)
                for check in checks:
                    punto=puntos[i]
                    print("------------pto-----------------")
                    print(punto)
                    i+=1
                    opcion=Opciones(pregunta=pregunta, opcion=check, puntaje=punto)
                    opcion.save()
            return redirect('/sistema/agregarEncuesta')
        else:
            pregunta_form=PreguntaForm()
            tipos=Tipo_Pregunta.objects.all()
        return render(request,'sistema/agregarPregunta.html',{'pregunta_form':pregunta_form,'tipos':tipos})
    else:
        return redirect('home')

@login_required
def validarPregunta(request):
    nombre = request.GET.get('nombre')
    data = {
        'is_taken': Pregunta.objects.filter(descripcion=nombre,borrado=False).exists()
    }
    if data['is_taken']:
        data['error_message']  = 'Esta Pregunta ya existe, por favor haz otra pregunta'
    print(data)
    return JsonResponse(data)

@login_required
def eliminarPregunta(request,id_pregunta):
    if permiso(request, 26):  
        pregunta=Pregunta.objects.get(id_pregunta=id_pregunta)
        opciones=Opciones.objects.filter(pregunta_id=id_pregunta)
        for opcion in opciones:
            opcion.borrado=True
            opcion.save()
        pregunta.borrado=True
        pregunta.save()
        return redirect('/sistema/agregarEncuesta/')
    else:
        return redirect('home')

@login_required
def agregarRespuesta(request):
    miembro=Miembro.objects.get(dni=request.user.miembro_id)
    if(Encuesta.objects.filter(miembro_id=miembro,respondio=False)).exists():
        encuesta=Encuesta.objects.filter(miembro_id=request.user.miembro_id,respondio=False).last()
        print(encuesta)
        # encuesta=Encuesta.objects.get()
        preguntas=encuesta.tipo.preguntas.filter(borrado=False)
        print('tene si una pendiente ameo')
        reunion = encuesta.reunion
    else:
        messages.error(request, 'NO TIENE ENCUESTAS PENDIENTES') 
        return redirect('home')

    if request.method == 'POST':
        if encuesta.tipo.id_tipo_encuesta ==1:
            puntos=0
            for pregunta in preguntas: 
                opcion=request.POST.get(str(pregunta.id_pregunta))
                print('----------------------------')
                print(opcion)
                print('---------------')
                if pregunta.tipo.id_tipo_pregunta==1: #es una pregunta abierta, no suma puntos, y por cada pregunta abierta creo una nueva respuesta
                    opcion=Opciones(borrado=False,pregunta_id=pregunta.id_pregunta,opcion=opcion,puntaje=0)
                    opcion.save()
                    respuesta=Respuesta(pregunta=pregunta,borrado=False,encuesta=encuesta,opcion=opcion)
                    respuesta.save()        
                else:
                    opcion=Opciones.objects.filter(borrado=False,pregunta_id=pregunta.id_pregunta,opcion=opcion).first()
                    #busco la opcion que coincida con la opcion que me mandaron por el request.POST
                    respuesta=Respuesta(pregunta=pregunta,borrado=False,encuesta=encuesta,opcion=opcion)
                    puntos+=opcion.puntaje
                    respuesta.save()
            fecha=date.today()
            encuesta.fecha_respuesta=fecha
            encuesta.respondio=True
            encuesta.puntaje=puntos
            encuesta.save()
            reunion=encuesta.reunion.id_reunion
            cant=encuesta.tipo.cantidad
            asistencias=Asistencia.objects.filter(miembro=miembro,justificado=False,reunion_id=reunion).order_by('fecha')[:cant]
            for ast in asistencias:    
                ast.justificado=True
                ast.save()
        if encuesta.tipo.id_tipo_encuesta==3:
            puntos=0
            for pregunta in preguntas: 
                opcion=request.POST.get(str(pregunta.id_pregunta))
                print('----------------------------')
                print(opcion)
                print('---------------')
                if pregunta.tipo.id_tipo_pregunta==1: #es una pregunta abierta, no suma puntos, y por cada pregunta abierta creo una nueva respuesta
                    opcion=Opciones(borrado=False,pregunta_id=pregunta.id_pregunta,opcion=opcion,puntaje=0)
                    opcion.save()
                    respuesta=Respuesta(pregunta=pregunta,borrado=False,encuesta=encuesta,opcion=opcion)
                    respuesta.save()        
                else:
                    opcion=Opciones.objects.filter(borrado=False,pregunta_id=pregunta.id_pregunta,opcion=opcion).first()
                    #busco la opcion que coincida con la opcion que me mandaron por el request.POST
                    respuesta=Respuesta(pregunta=pregunta,borrado=False,encuesta=encuesta,opcion=opcion)
                    puntos+=opcion.puntaje
                    respuesta.save()
            fecha=date.today()
            encuesta.fecha_respuesta=fecha
            encuesta.respondio=True
            encuesta.puntaje=puntos
            encuesta.save()
            reunion=encuesta.reunion.id_reunion
            cant=encuesta.tipo.cantidad
            asistencias=Asistencia.objects.filter(miembro=miembro,justificado=False,reunion_id=reunion).order_by('fecha')[:cant]
            for ast in asistencias:    
                ast.justificado=True
                ast.save()
            #----Esto es el modulo inteligente para ver el estado de la personas
            #Bueno la persona termino de responder y pum tengo que determinar su estado... para eso que hago? 
            #bueno voy a ver las respuestas que esten dentro de esta encuesta, obtengo la pregunta y el tipo, si es abierta la ignoro, si es cerrada
            #agarro la que tenia maximo valor y sumo, una vez
            #si la pregunta es multiple sumo todos los valores, todo esto guardo en un puntos_total
            puntos_total=0
            respuestas=Respuesta.objects.filter(encuesta_id=encuesta.id_encuesta)
            print('respuestas: ',respuestas)
            for respuesta in respuestas:
                if respuesta.pregunta.tipo.id_tipo_pregunta==2: 
                    opt=Opciones.objects.filter(pregunta=respuesta.pregunta).aggregate(Max('puntaje'))
                    print('--------------------////////------------------')
                    opt=opt['puntaje__max']
                    print(opt)
                    print('--------------------////////------------------')
                    puntos_total+=opt
                if respuesta.pregunta.tipo.id_tipo_pregunta==3:
                    opt= Opciones.objects.filter(pregunta=respuesta.pregunta).aggregate(Sum('puntaje'))
                    print('--------------------////////------------------')
                    print(opt)
                    print('--------------------////////------------------')
                    puntos_total += opt
            #bien ahora tengo los puntos totales, lo que tengo que hacer es ver en que rango esa la persona y para ello facil
            #si obtuvo un puntaje mayor que la mitad de los puntos totales esta pasable
            #si obtuvo la mitad esta en control
            #si obtuvo cero deberia estar suspendido...
            #----------si obtuvo cero entra en juego mi modulo inteligente de reasignacion de miembros o lideres
            usuario=request.user.id
            print('puntos:',puntos_total)
            print('-----hasta aca llego--------')
            if puntos <= puntos_total/4:
                print('critico')
                #tengo que crear ese estado critico y que quede en la espera de confirmacion
                #para la baja
                est = Estado.objects.get(id=4)
                #critico sin confirmar es pendiente
                estado=Estado_Usuario(usuario=request.user,estado=est,confirmado=False) 
                estado.changeReason="Creacion"
                estado.save()
                mensaje=Mensaje.objects.get(tipo_id=3)
                asunto = mensaje.tipo.tipo
                mensaje = mensaje.mensaje + "se trata de " + request.user.miembro.apellido + ", " + request.user.miembro.nombre + ". Por favor ingrese en el siguiente enlace http://localhost:8000/sistema/reasignar/"+str(encuesta.miembro.dni)
                miembros=[]
                miembros.append(request.user.miembro)
                enviarMail(miembros, asunto, mensaje)
                mensaje=Mensaje.objects.get(tipo_id=3)
                mensaje=mensaje.mensaje
                enviarWhatsapp(mensaje,miembros)
                #aca pum ya notifico
            if puntos <= puntos_total/2 and puntos > puntos_total/4:
                print("Medio")
                est = Estado.objects.get(id=3)
                estado=Estado_Usuario(usuario=request.user,estado=est)
                estado.changeReason="Creacion"
                estado.save()
            if (puntos > puntos_total/2) and (puntos <= (puntos_total-(puntos_total/4))):
                print("Bueno")
                est = Estado.objects.get(id=2)
                estado=Estado_Usuario(usuario=request.user,estado=est)
                estado.changeReason="Creacion"
                estado.save()
                
            if (puntos > (puntos_total-(puntos_total/4))) and (puntos <= puntos_total):
                print('Re bien!!')
                est = Estado.objects.get(id=1)
                estado=Estado_Usuario(usuario=request.user,estado=est)
                estado.changeReason="Creacion"
                estado.save()
            
        return redirect('home')

    return render(request,'sistema/agregarRespuesta.html',{'preguntas':preguntas,'reunion':reunion})

def agregarRespuestaReunion(request,id_encuesta):  
    encuesta=Encuesta.objects.get(id_encuesta=id_encuesta)
    print('-------encuesta: ',encuesta.tipo.preguntas.all())
    preguntas=encuesta.tipo.preguntas.all()
    reunion = encuesta.reunion
    
    if request.method == 'POST':
        puntos=0
        for pregunta in preguntas: 
            opcion=request.POST.get(str(pregunta.id_pregunta))
            print('----------------------------')
            print(opcion)
            print('-----------------------------')
            if pregunta.tipo.id_tipo_pregunta==1: #es una pregunta abierta, no suma puntos, y por cada pregunta abierta creo una nueva respuesta
                opcion=Opciones(borrado=False,pregunta_id=pregunta.id_pregunta,opcion=opcion,puntaje=0)
                opcion.save()
                respuesta=Respuesta(pregunta=pregunta,borrado=False,encuesta=encuesta,opcion=opcion)
                respuesta.save()        
            else:
                opcion=Opciones.objects.filter(borrado=False,pregunta_id=pregunta.id_pregunta,opcion=opcion).first()
                #busco la opcion que coincida con la opcion que me mandaron por el request.POST
                respuesta=Respuesta(pregunta=pregunta,borrado=False,encuesta=encuesta,opcion=opcion)
                puntos+=opcion.puntaje
                
                respuesta.save()
        fecha=date.today()
        encuesta.fecha_respuesta=fecha
        encuesta.respondio=True
        encuesta.puntaje=puntos
        encuesta.save()
            #----Esto es el modulo inteligente para ver el estado de la Reunion
            #Bueno la persona termino de responder y pum tengo que determinar su opinion... para eso que hago? 
            #bueno voy a ver las respuestas que esten dentro de esta encuesta, obtengo la pregunta y el tipo, si es abierta la ignoro, si es cerrada
            #agarro la que tenia maximo valor y sumo, una vez
            #si la pregunta es multiple sumo todos los valores, todo esto guardo en un puntos_total
        puntos_total=0
        respuestas=Respuesta.objects.filter(encuesta_id=encuesta.id_encuesta)
        print('respuestas: ',respuestas)
        for respuesta in respuestas:
            if respuesta.pregunta.tipo.id_tipo_pregunta==2: 
                opt=Opciones.objects.filter(pregunta=respuesta.pregunta).aggregate(Max('puntaje'))
                #print('--------------------////////------------------')
                opt=opt['puntaje__max']
                # print(opt)
                # print('--------------------////////------------------')
                puntos_total+=opt
            if respuesta.pregunta.tipo.id_tipo_pregunta==3:
                opt= Opciones.objects.filter(pregunta=respuesta.pregunta).aggregate(Sum('puntaje'))
                # print('--------------------////////------------------')
                # print(opt)
                # print('--------------------////////------------------')
                puntos_total += opt
            #bien ahora tengo los puntos totales, lo que tengo que hacer es ver en que rango esta la reunion y para ello facil
            #si obtuvo un puntaje mayor que la mitad de los puntos totales esta pasable
            #si obtuvo la mitad esta en control
            #si obtuvo cero deberia estar suspendido...
            #----------si obtuvo cero entra en juego mi modulo inteligente de reasignacion de miembros o lideres
        print('puntos encuestas: ', puntos)
        print('puntos totales:',puntos_total)
        print('-----hasta aca llego--------') #mi modulito xd
        #a partir de aca tengo que crear un registro por persona que respondio
        reunion=encuesta.reunion
        if puntos <= puntos_total/4:
            print('critico')
            est = Estado.objects.get(id=4) #estado Critico
            estado=Estado_Reunion(estado=est,reunion=reunion,encuesta = encuesta)
            estado.save()
            #si no le informo nunca se entera que su reunion esta en estado critico...

        if puntos <= puntos_total/2 and puntos > puntos_total/4:
            print("medio")
            est = Estado.objects.get(id=3) #estado Medio
            estado=Estado_Reunion(estado=est,reunion=reunion,encuesta = encuesta)
            estado.save()
        if (puntos > puntos_total/2) and (puntos <= (puntos_total-(puntos_total/4))):
            print("Bueno")
            est = Estado.objects.get(id=2) #Estado Bueno
            estado=Estado_Reunion(estado=est,reunion=reunion,encuesta = encuesta)
            estado.save()
        if (puntos > (puntos_total-(puntos_total/4))) and (puntos <= puntos_total):
            print('Re bien!!')
            est = Estado.objects.get(id=1) #estado muy Bueno
            estado=Estado_Reunion(estado=est,reunion=reunion,encuesta = encuesta)
            estado.save()
        return redirect('home')    

    print('Preguntas: ', preguntas)
    print('reunion: ', reunion)
    return render(request,'sistema/agregarRespuesta.html',{'preguntas':preguntas,'reunion':reunion})

@login_required
def recomendacion(request):
    #Bien ahora si la idea es obtener todas las encuestas enviadas a esa reunion en esa fecha
    #ver cuantos respondieron y que respondieron si respondio
    rn = request.GET.get('rn')
    reunion = Reunion.objects.get(id_reunion=rn)
    cant_m=0  #cantidad de estados medios
    cant_c=0  #cantidad de estados criticos
    cant_total=0
    data= []
    preguntas=[]
    opciones=[]
    mejora = None
    encuesta = Encuesta.objects.filter(reunion_id=reunion.id_reunion,tipo=2).exclude(fecha_respuesta=None).order_by('-fecha_envio').first()#ahora obtengo todas la ultima que envie
    if encuesta !=None:
        fecha_envio = encuesta.fecha_envio
        encuestas = Encuesta.objects.filter(reunion_id=reunion.id_reunion,tipo=2,fecha_envio=fecha_envio).exclude(fecha_respuesta=None) #con respuestas
        cant_total=len(list(encuestas)) #cantidad de encuestas enviadas a esa rn en esa fecha con respuestas
    
    if cant_total == 0: #si nadie respondio todavia
        data=[]
    else:
        for encuesta in encuestas: #por cada encuesta que respondio
            estado= Estado_Reunion.objects.filter(encuesta_id=encuesta.id_encuesta,reunion_id=rn).last()
            if estado.estado_id == 3:
                cant_m += 1
                #aca tengo que ver que le hizo estar en este estado
                #para eso voy a obtener las respuestas de esta encuesta
                respuestas = Respuesta.objects.filter(encuesta_id=encuesta.id_encuesta)
                for respuesta in respuestas:
                    #por cada respuesta voy a ver sus opciones
                    if respuesta.opcion.puntaje==0 and respuesta.pregunta.tipo.id_tipo_pregunta!=1:
                        if not(respuesta.pregunta in preguntas): #si la pregunta no esta aca la agrego
                            preguntas.append(respuesta.pregunta)
                            opciones.append(respuesta.opcion)
            if estado.estado_id == 4 :
                cant_c += 1
                #aca tengo que ver que le hizo estar en este estado
                #para eso voy a obtener las respuestas de esta encuesta
                respuestas = Respuesta.objects.filter(encuesta_id=encuesta.id_encuesta)
                for respuesta in respuestas:
                    #por cada respuesta voy a ver sus opciones
                    if respuesta.opcion.puntaje==0 and respuesta.pregunta.tipo.id_tipo_pregunta!=1:
                        if not(respuesta.pregunta in preguntas): #si la pregunta no esta aca la agrego
                            preguntas.append(respuesta.pregunta)
                            opciones.append(respuesta.opcion)
        


        #-------Bien ahora tendria que ver su estado anterior( :c ) ----- para ver si presenta mejoras

        puntos_negativos = 0
        enc = Encuesta.objects.filter(reunion_id=reunion.id_reunion,tipo=2,fecha_envio__lte=fecha_envio).exclude(fecha_envio=fecha_envio).first() #ahora obtengo la ante ultima que envie
        c =0
        if enc != None:
            fecha_envio = enc.fecha_envio
            encuestas = Encuesta.objects.filter(reunion_id=reunion.id_reunion,tipo=2,fecha_envio=fecha_envio).exclude(fecha_respuesta=None) #con respuestas
            c=len(list(encuestas)) #cantidad de encuestas enviadas a esa rn en esa fecha con respuestas
        if c != 0: #si alguien respondio 
            for encuesta in encuestas: #por cada encuesta que respondio
                estado= Estado_Reunion.objects.filter(encuesta_id=encuesta.id_encuesta,reunion_id=rn).last()
                if estado.estado_id == 3:
                    puntos_negativos +=1
                if estado.estado_id == 4:
                    puntos_negativos +=1
            if (puntos_negativos > (cant_m + cant_c)): # si los pontajes negativos de la ante ultima son mayores que los de la ultima entonces mejoro
                mejora = True
            else:
                mejora = False

        if cant_m or cant_c: #si alguno de estos no esta vacio tiene que haber recomendaciones
            i=0
            for reco in preguntas:
                dic={'mejora':mejora, 'pregunta':reco.descripcion,'opcion':opciones[i].opcion} #si hubo True, sino False,  y si no hay estado para comparar None
                i+=1
                data.append(dic)

    print("-----------------------------//-----------------------")
    print('data: ',data)
    return JSONResponse(data)

@login_required
def verRespuesta(request,id_encuesta):
    if permiso(request, 30):
        encuesta=Encuesta.objects.get(id_encuesta=id_encuesta)
        respuestas=Respuesta.objects.filter(encuesta=encuesta)
        if request.method =='POST':
            return redirect('home')
        return render(request,'sistema/verRespuesta.html',{'respuestas':respuestas})
    else:
        return redirect('home')

@login_required
def reasignar(request,dni):
    miembro=Miembro.objects.get(dni=dni)
    usr=CustomUser.objects.get(miembro__dni=dni)
    print('Encargado: ', usr)
    reuniones=[]
    grupos = Grupo.objects.filter(encargado = usr.id).exclude(borrado=True)
    print('Grupos: ', grupos)
    for grupo in grupos:
        rns = Reunion.objects.filter(grupo_id=grupo.id_grupo)
        print('rns: ', rns)
        for rn in rns:
            if not(rn in reuniones):
                reuniones.append(rn) 
    print('Reuniones: ',reuniones)
    if request.method=='POST':
        if 'confirm' in request.POST:
            print(request.POST)
            for reunion in reuniones:
                miembros=reunion.grupo.miembro.all()
                for miembro in miembros:
                    nombre = miembro.apellido + ', ' + miembro.nombre
                    reuniones_encargado=request.POST.getlist('reunion-encargado '+nombre)
                    print('------------------//-----------------------------')
                    print('reuniones:',reuniones_encargado) #esto devuelve toda una lista que la voy a ir cortando
                    print('')
                    if reuniones_encargado:
                        for reunion_cambio in reuniones_encargado: 
                            rn,mb=reunion_cambio.split("-") #reunion uso para cortar no mas reunion tiene esto "id_r+id_m"
                            print("rn-mb",rn,mb)
                            #tengo que buscar esta reunion y ese miembro
                            rn=Reunion.objects.get(id_reunion=rn)
                            mb=Miembro.objects.get(dni=mb)
                            #Bien, aca empieza la reasignacion de miembros y el envio de correo para los encargados, vamos a empezar reasignando miembros
                            #Hay que ver si el miembro ya no es parte de esa reunion
                            #primero obtengo el grupo de la reunion
                            if mb in rn.grupo.miembro.all(): #si el miembro esta en la rn
                                print('ya ta')
                            else:
                                rn.grupo.miembro.add(mb)
                                rn.grupo.changeReason='Modificacion' 
                                rn.grupo.save()
                                #es hora de avisar!
                                msj=Mensaje.objects.get(tipo_id=5)
                                mensaje=msj.mensaje
                                miembros=[]
                                usr=CustomUser.objects.get(id=rn.grupo.encargado)
                                mb_new=Miembro.objects.get(dni=usr.miembro_id)
                                miembros.append(mb_new)
                                asunto = msj.tipo
                                enviarWhatsapp(mensaje,miembros)
                                mensaje = mensaje + 'El miembro ' + miembro.nombre + 'fue añadido a tu reunion ' + rn.nombre 
                                enviarMail(miembros,asunto,mensaje)
                                #hasta aca avisamos al lider, ahora vamos al mb
                                miembros.clear()
                                miembros = []
                                miembros.append(miembro)
                                msj=Mensaje.objects.get(tipo_id=5)
                                mensaje=msj.mensaje + ' Fuiste añadido a una nueva reunion'
                                enviarWhatsapp(miembros,mensaje) #le mandamos whatsapp
                                mensaje = msj.mensaje + 'Fuiste añadido a la reunion ' + rn.nombre + ' habla con ' + mb_new.nombre +' para mas informacion'
                                enviarMail(miembros,asunto,mensaje)
                    
            for reunion in reuniones:
                if request.POST.get(reunion.nombre+'-encargado') != None :
                    encargado=request.POST.get(reunion.nombre+'-encargado')
                    print('encargado: ',encargado)
                    if CustomUser.objects.filter(miembro_id=encargado).exists():
                        print('entre al if china')
                        enc=CustomUser.objects.get(miembro__dni=encargado)
                        reunion.grupo.encargado=enc.id
                        reunion.grupo.save()
                    else:
                        print('hay un encargado pero no es un usr ', encargado)
                        #Weno aca no se que hacer
                else: #si no tienen un nuevo encargado bye bye
                    reunion.borrado = True
                    reunion.changeReason='Eliminacion'
                    reunion.save()
                    reunion.grupo.borrado= True
                    #vacio tmb el grupo, porque si quiere reactivar la reunion tendra miembros nuevos
                    #dejo el encargado?
                    reunion.grupo.miembro.clear() #tengo miedo
                    reunion.grupo.changeReason='Elimincaion'
                    reunion.grupo.save()
            usr.is_active=False
            if Estado_Usuario.objects.filter(estado_id=4,confirmado=False,usuario_id = usr.id).exists():
                estado = Estado_Usuario.objects.filter(estado_id=4,confirmado=False,usuario_id = usr.id).last()
                estado.confirmado = True
                usr.changeReason = "Modificacion" #se desactivo
                estado.changeReason = "Modificacion"
                estado.save()
            usr.changeReason="Modificacion"
            usr.save()
            return redirect('home')
        if 'cancelar' in request.POST:
            #dejo el estado en pendiente, hasta que el admin personalmente lo cambie
            return redirect('/sistema/listarUsuario')
    
    return render(request,'sistema/reasignar.html',{'miembro':miembro,'reuniones':reuniones})

@login_required
def crearRol(request):
    if permiso(request, 31):
        if request.method=='POST':
            nombre=request.POST.get('nombre')
            rol=Rol(nombre=nombre,borrado=False)
            rol.save()
            rol.permisos.set(request.POST.getlist('permisos'))
            rol.save()
            return redirect('home')
        else:
            permisos=Permisos.objects.all()
            rol_form=RolForm()
            return render(request,'sistema/crearRol.html',{'rol_form':rol_form,'permisos':permisos})
    else:
        return redirect('home') 

@login_required
def verRol(request):
    if permiso(request, 32):
        roles=Rol.objects.filter(borrado=False)
        configuracion_form = Configuracion.objects.all().last()
        return render(request,'sistema/verRol.html',{'roles':roles,'configuracion_form':configuracion_form})
    else:
        return redirect('home')

@login_required
def editarRol(request,id_rol):
    if permiso(request, 34):
        rol=Rol.objects.get(id_rol=id_rol)
        if request.method =="POST":
            nombre=request.POST.get('nombre')
            rol.nombre=nombre
            permisos=request.POST.getlist('permisos')
            permisos=Permisos.objects.filter(id_permiso__in=permisos)
            rol.permisos.set(permisos)
            rol.save()
            return redirect('home')
        else:
            rol_form=RolForm(instance=rol)
            permisos=rol.permisos.all()
            permisos_excluidos = Permisos.objects.exclude(id_permiso__in=permisos)
            return render(request,'sistema/editarRol.html',{'rol_form':rol_form,'permisos':permisos,'permisos_excluidos':permisos_excluidos})
    else:
        return redirect('home')

@login_required
def eliminarRol(request,id_rol):
    if permiso(request, 33):
        rol=Rol.objects.get(id_rol=id_rol)
        if CustomUser.objects.filter(rol = rol).exists():
            messages.error(request, 'NO SE PUEDE ELIMINAR EL ROL: existen usuarios con dicho rol') 
            return redirect('/sistema/verRol')
        else:
            rol.borrado=True
            rol.save()
            return redirect('/sistema/verRol/')
    else:
        return redirect('home')

@login_required
def validarRol(request):
    nombre = request.GET.get('nombre')
    data = {
        'is_taken': Rol.objects.filter(nombre=nombre,borrado=False).exists()
    }
    if data['is_taken']:
        rol=Rol.objects.filter(nombre=nombre).last()
        print(rol)
        rol=Rol.objects.get(id_rol=rol.id_rol)
        if rol.borrado==True:
            data['error_message'] = 'Este nombre de rol ya existe, pero fue borrado, vaya "ver roles" y editar, o elija otro nombre'
        else:
            data['error_message']  = 'Este nombre de rol ya existe, por favor elige otro nombre'
    print(data)
    return JsonResponse(data)

@login_required
def auditoria_detalles_miembro(request,dni,id_auditoria):
    print(dni, id_auditoria)
    mb_historial = Miembro.history.filter(dni=dni)
    historial = Miembro.history.filter(dni=dni)
    print(historial)
    if len(mb_historial) > 1: #weno si hay algo
        for i in range(len(historial)): #recorro lo que hay
            print(id_auditoria, " - ", historial[i].dni)
            if historial[i].history_id == id_auditoria:  
                print("entro al if")          
                audit_regsolo = historial[i]    
                delta = audit_regsolo.diff_against(mb_historial[i+1])
                print(delta)
                data = []            
                for change in delta.changes:
                    dic = {'change': change.field, 'old':change.old, 'new':change.new}
                    data.append(dic)
                    print("Entro en el for")
                    print(data)
                break
            else:
                data = []
    else:
        data=[{'change':False}]
    print("DATA: ", data)
    return JSONResponse(data)

@login_required
def auditoria_detalles_reunion(request,id,id_auditoria):
    print(id, id_auditoria)
    rn_historial = Reunion.history.filter(id_reunion=id)
    historial = Reunion.history.filter(id_reunion=id)
    print(historial)
    if len(rn_historial) > 1:
        for i in range(len(historial)): 
            print(id_auditoria, " - ", historial[i].history_id)
            if historial[i].history_id == id_auditoria:  
                print("entro al if")          
                audit_regsolo = historial[i]    
                delta = audit_regsolo.diff_against(rn_historial[i+1])
                print(delta)
                data = []            
                for change in delta.changes:
                    dic = {'change': change.field, 'old':change.old, 'new':change.new}
                    data.append(dic)
                    print("Entro en el for")
                    print(data)
                break
            else:
                data = []
    else:
        data=[{'change':False}]
    print("DATA: ", data)
    return JSONResponse(data)

@login_required
def auditoria_detalles_asistencia(request,id_asistencia,id_auditoria):
    auditoria_historial = Asistencia.history.filter(id_asistencia=id_asistencia)
    historial = Asistencia.history.filter(id_asistencia=id_asistencia)
    if len(auditoria_historial) > 1:
        for i in range(len(historial)): 
            if historial[i].history_id == id_auditoria:  
                audit_regsolo = historial[i]    
                delta = audit_regsolo.diff_against(auditoria_historial[i+1])
                data = []            
                for change in delta.changes:
                    dic = {'change': change.field, 'old':change.old, 'new':change.new}
                    data.append(dic)
                break
            else:
                data = []
    else:
        data=[{'change':False}]
    return JSONResponse(data)    

@login_required
def enviarMensaje(request):
    reuniones=Reunion.objects.filter(borrado=False)
    if request.method == 'POST':
        rns=request.POST.getlist('rn')
        print(rns)
        if 'Todos' in rns:
            miembros = Miembro.objects.filter(borrado=False)
            mensaje=request.POST.get('mensaje')
            enviarWhatsapp(mensaje,miembros)
        else:
            for reunion in rns:
                reunion=Reunion.objects.get(id_reunion=reunion)
                miembros = reunion.grupo.miembro.all()
                mensaje=request.POST.get('mensaje')
                enviarWhatsapp(mensaje,miembros)
        print('en teoria envio')
    return render(request,'sistema/enviarMensaje.html',{'reuniones':reuniones})

@login_required
def listarUsuario(request):
    configuracion_form = Configuracion.objects.all().last()
    usuarios = CustomUser.objects.exclude(id=request.user.id)
    context ={'usuarios':usuarios,'configuracion_form':configuracion_form,'usuarios':usuarios}
    return render(request,'sistema/listarUsuario.html',context)

@login_required
def reactivarUsuario(request,id):
    if permiso(request, 36):
        usuario = CustomUser.objects.get(id=id)
        est=Estado.objects.get(id=1)
        estado = Estado_Usuario(estado=est,confirmado=True,usuario_id = usuario.id)
        estado.changeReason = "Reactivacion"
        estado.save()
        usuario.is_active=True
        usuario.changeReason = "Modificacion"
        usuario.save()
        return redirect('/sistema/listarUsuario')

@login_required
def configurarUsuario(request,id):
    user=CustomUser.objects.get(id=id)
    if request.user.id == user.id:
        contra=True  #me estoy queriendo editar a mi, por lo tanto puedo editar mi contrania
    else:
        contra=False
    if permiso(request, 34): #si tengo permisos para cambiar roles
        permi=True
    else:
        permi=False
    if request.method == "POST":
        if 'change' in request.POST:
            passV = request.POST.get('inputPassword4', None)#pass vieja
            nuevapass = request.POST.get('inputPassword6', None)
            nuevapassVer = request.POST.get('inputPassword8', None) #la repe de la pass nueva
            if passV=="" or nuevapass=="" or nuevapassVer=="":
                messages.error(request, "Debe cargar todos los datos requeridos para cambiar la contraseña")
                form = CustomUserCreationForm(request.POST) #se va a redirigir bien abajo pero le paso los datos que ya tenia
            else:
                usuario = authenticate(username=request.user.username, password=passV)
                if nuevapass == nuevapassVer:
                    iguales = True
                    if (usuario is not None):
                        request.user.set_password(nuevapass)
                        request.user.save()
                        form = CustomUserCreationForm(instance=user)
                        return redirect('home')
                    else:
                        messages.error(request, "Constraseñas incorrectas")
                        form = CustomUserCreationForm(request.POST)
                        return render(request,'sistema/configuracion_usr.html',{'form':form,'permi':permi,'contra':contra})
                else:
                    messages.error(request, "Las Constraseñas no coinciden")
                    form = CustomUserCreationForm(request.POST)
                    return render(request,'sistema/configuracion_usr.html',{'form':form,'permi':permi,'contra':contra})

        if 'confirmar' in request.POST:
            username = request.POST.get('username', None)
            email = request.POST.get('email', None)
            rl = request.POST.get('rol', None)
            rol = Rol.objects.get(id_rol=rl)
            user.username = username
            user.email = email
            user.rol = rol
            user.save()
            try:
                if permiso(request, 38):
                    return redirect('/sistema/listarUsuario')
            except:
                return redirect('home')
            #aca podria irse al listar usr si tiene permiso, sino al home
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request,'sistema/configuracion_usr.html',{'form':form,'permi':permi,'contra':contra})

@csrf_exempt
def mail(request):
    dni = request.GET.get('dni') 
    miembro = Miembro.objects.get(dni=dni)
    mail=""
    if miembro.correo:
        mail=miembro.correo #tiene que tener mail si o si
    return JSONResponse(mail)

@csrf_exempt
def provinciasList(request):
    if request.method == 'GET': #uso para reuniones y miembros
        provincia = Provincia.objects.all()
        serializer = ProvinciaSerializer(provincia, many=True)
        result = dict()
        result = serializer.data
        return JSONResponse(result)

@csrf_exempt
def localidadesList(request):
    pv=request.GET.get('provincia',None) #uso para reuniones y miembros
    prov=Provincia.objects.get(provincia=pv)
    if request.method == 'GET':
        localidad = Localidad.objects.filter(provincia=prov).order_by('localidad')
        serializer = LocalidadSerializer(localidad, many=True)
        result = dict()
        result = serializer.data
        return JSONResponse(result)

@csrf_exempt
def barriosList(request):
    lc=request.GET.get('localidad',None) #uso para reuniones y miembros
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
    print(request.GET) #Uso para agregar Asistencias
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
def miembroTable(request):
    print('entro en miembroTable') #Voy a usar para hacer filtros de edades y de sexo en crear grupo
    sx = request.GET.get('sx')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    #tengo que ver los anhos si quiero tenes un grupo desde los 15 hasta los 20 por ej
    hoy = date.today()
    #el hasta es mas chico que el desde, por lo tanto para filtrar un fecha de nac tiene que estar entre
    # fecha__range(f_min,f_max)
    #donde f_min = al hasta anho 2000 y la f_max va a ser 2005 seria el desde
    dif = hoy.year - int(hasta)
    f_min = date(int(dif),12,31)
    dif = hoy.year - int(desde)
    f_max = date(int(dif),12,31)
    print('sx ', sx)
    print('desde ', f_min)
    print('hasta ', f_max)
    if request.method == 'GET':
        if sx != 'Ambos':
            miembros=Miembro.objects.filter(sexo = sx, fecha_nacimiento__range=(f_min,f_max))
        else:
            miembros=Miembro.objects.filter(fecha_nacimiento__range=(f_min,f_max))
        print(miembros)
        serializer = MiembroSerializer(miembros, many=True)
        result = dict()
        result = serializer.data
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

@csrf_exempt
def EncuestaTable(request):
    #tp=Request.POST.get('tp',None)
    encuesta=Encuesta.objects.last()
    if request.method == 'GET':
        serializer = EncuestaSerializer(encuesta, many=True)
        result = dict()
        result = serializer.data
        #print("No ta")
        return JSONResponse(result)

@csrf_exempt
def opcionesList(request):
    pr=request.GET.get('pr')
    print('pr:  ',pr)
    if request.method == 'GET':
        pregunta=Pregunta.objects.get(id_pregunta=pr)
        if pregunta.tipo_id==1:
            if Opciones.objects.filter(borrado=False,pregunta_id=pr).exists():
                opciones=Opciones.objects.filter(borrado=False,pregunta_id=pr)[:1]
            else:
                opciones= Opciones(pregunta=pregunta,opcion="Abierta",puntaje=0)
                opciones.save()
        else:
            opciones=Opciones.objects.filter(borrado=False,pregunta_id=pr)
        serializer=OpcionesSerializer(opciones,many=True)
        result=dict()
        result = serializer.data
        return JSONResponse(result)

@csrf_exempt
def respuestaList(request):
    rs=request.GET.get('rs')
    if request.method=='GET':
        print('------------//------------')
        print('rs: ',rs)
        respuesta= Respuesta.objects.get(id_respuesta=rs)
        serializer=RespuestaSerializer(respuesta,many=False)
        result=dict()
        result = serializer.data
        print(result)
        return JSONResponse(result)

@csrf_exempt
def recomendacionTable(request):
    rn=request.GET.get('rn')
    if request.method =='GET':
        reunion=Reunion.objects.get(nombre=rn)
        best_usr_recomendados=[] #horario,domicilio,sexo == al actual
        usr_recomendados=[]
        mb_recomendados=[]
        encargado=reunion.grupo.encargado
        usr_encargado=CustomUser.objects.get(id=encargado)
        mb_encargado=usr_encargado.miembro
        miembro= CustomUser.objects.get(id=1)
        dic=[]
        data=[]
        #bueno la idea ahora es ver en que horario se da esta reunion y ver que usuario tiene libre ese horario
        #si ninguno tiene, entonces vemos el domicilio, a ver a quien le queda mas cerca
        #y ver a que grupo de personas atiende esa persona tmb, por ejemplo si el grupo es femenino vemos una chica
        hs_rn=reunion.horario
        if Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta).exists():
            horarios=Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta)
            for horario in horarios:
                if Miembro.objects.filter(horario_disponible=horario).exclude(dni=mb_encargado.dni).exists():
                    miembros=Miembro.objects.filter(horario_disponible=horario).exclude(dni=mb_encargado.dni)
                    #bien aca traje todos los miembros que tienen ese hs disponible a continuacion veo si hay un usr
                    for miembro in miembros:
                        if CustomUser.objects.filter(miembro=miembro.dni).exists():
                            usrs=CustomUser.objects.filter(miembro=miembro.dni)
                            for usr in usrs: #por cada usuario que tenga asosiado un miembro con horario disponible
                                # si concide el sexo del mb con el del grupo o si grupo admite ambos,funciona para femenino o masculino
                                if usr.miembro.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos": #si los sexos coinciden entonces recomiendo
                                    if usr.miembro.domicilio.barrio == reunion.domicilio.barrio:
                                        if not(miembro in best_usr_recomendados) and not(miembro in usr_recomendados):
                                            best_usr_recomendados.append(miembro) #el mejor
                                            nombre= miembro.apellido +", "+miembro.nombre
                                            motivos=['Es un Usuario','Cuenta con Horario Disponible','Mismo Barrio','Mismo Sexo que el grupo']
                                            dic={'dni':miembro.dni,'miembro': nombre, 'motivos':motivos}
                                            data.append(dic)
                                    else:
                                        if not(miembro in usr_recomendados) and not(miembro in best_usr_recomendados):
                                            usr_recomendados.append(miembro) #no es tan weno
                                            nombre= miembro.apellido +", "+miembro.nombre
                                            motivos=['Es un Usuario','Cuenta con Horario Disponible','Mismo Sexo que el grupo']
                                            dic={'dni':miembro.dni,'miembro': nombre, 'motivos':motivos}
                                            data.append(dic)
                        else: #aca no hay ningun user, entonces... vamos por miembros del mismo genero
                                if miembro.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos":
                                    if not(miembro in usr_recomendados) and not(miembro in best_usr_recomendados):
                                        mb_recomendados.append(miembro)
                                        nombre= miembro.apellido +", "+miembro.nombre
                                        motivos=['Cuenta con Horario Disponible','Mismo Sexo que el grupo']
                                        dic={'dni':miembro.dni,'miembro': nombre, 'motivos':motivos}
                                        data.append(dic) 
                
                else: #osea si ningun MIEMBRO tiene hs disponibles
                    #pregunto por el domicilio, por el barrio no mas
                    dm_rn= reunion.domicilio
                    domicilios=Domicilio.objects.filter(barrio=dm_rn.barrio) #obtengo todos los domicilios que tiene ese barrio
                    for domicilio in domicilios: 
                        if Miembro.objects.filter(domicilio__barrio= domicilio.barrio).exclude(dni = request.user.miembro.dni).exists(): #veo si algun mb esta en el barrio
                            miembros=Miembro.objects.filter(domicilio__barrio= domicilio.barrio).exclude(dni = request.user.miembro.dni)
                            for miembro in miembros: #los miembros que tienen el mismo barrio y a hora veo si hay algun usr
                                if CustomUser.objects.filter(miembro=miembro.dni).exclude(miembro = request.user.miembro).exists(): #veo si alguno de esos miembros es un usr
                                    usrs=CustomUser.objects.filter(miembro=miembro.dni).exclude(miembro = request.user.miembro)
                                    for usr in usrs: #por cada usuario que tenga asosiado un miembro con el domicilio en ese barrio
                                        miembro = usr.miembro
                                        # si concide el sexo del mb con el del grupo o si grupo admite ambos,funciona para femenino o masculino
                                        if miembro.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos": #si los sexos coinciden entonces recomiendo
                                            if not(miembro in usr_recomendados) and not(miembro in best_usr_recomendados):
                                                usr_recomendados.append(miembro)
                                                nombre= miembro.apellido +", "+miembro.nombre
                                                motivos=['Es un Usuario','Mismo Barrio','Mismo Sexo que el grupo']
                                                dic={'dni':miembro.dni,'miembro': nombre, 'motivos':motivos}
                                                data.append(dic)  
                                            #aca no pregunto por el domicilio porque ya tamos en el domicilio XD osea no es best porque no tiene hs disponible
                                else: #aca hay cura, no tienen hs disponible, no hay usr, pero hay miembros en ese barrio
                                    if miembro.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos":
                                        if not(miembro in mb_recomendados):
                                            mb_recomendados.append(miembro) #esto ya es para la ultima opcion
                                            nombre= miembro.apellido +", "+miembro.nombre
                                            motivos=['Mismo Barrio','Mismo Sexo que el grupo']
                                            dic={'dni':miembro.dni,'miembro': nombre, 'motivos':motivos} 
                                            data.append(dic) 
                                        
                        else: #aca no tienen ni hs ni domicilio nadie de nadie osea fritos #pero no es el ultimo ciclo lina
                            print('')
        if not(best_usr_recomendados): 
            if not(usr_recomendados):
                #en este punto tengo todavia: reunion(que es la base siempre),usr_encargado,mb_encargado y las listas
                #puedo ver el rango etario xd, pero tiene que ser del mismo sexo y tipo si o si
                if Grupo.objects.filter(desde__gte=reunion.grupo.desde,hasta__lte=reunion.grupo.hasta,sexo=reunion.grupo.sexo).exclude(id_grupo=reunion.grupo.id_grupo).exists():
                    grupos_etarios = Grupo.objects.filter(desde__gte=reunion.grupo.desde,hasta__lte=reunion.grupo.hasta,sexo=reunion.grupo.sexo).exclude(id_grupo=reunion.grupo.id_grupo) 
                    #excluyo el grupo actual porque es el que necesita ser reubicado
                    for grupito in grupos_etarios:
                        en=CustomUser.objects.get(id=grupito.encargado) #en=encargado
                        mb=en.miembro
                        if not(mb in usr_recomendados) and not(mb in best_usr_recomendados):
                            usr_recomendados.append(mb)
                            nombre= mb.apellido +", "+mb.nombre
                            motivos=['Es un Usuario','Mismo Sexo que el grupo','Atiende el mismo grupo etario']
                            dic={'dni':mb.dni,'miembro': nombre, 'motivos':motivos}
                            data.append(dic)  
                if not(usr_recomendados) and not(mb_recomendados): #aca si que no hay nada de nada, entonces vamos a darle usr del mismo genero
                    if CustomUser.objects.filter(miembro__sexo=reunion.grupo.sexo).exclude(id=request.user.id).exists():
                        usrs=CustomUser.objects.filter(miembro__sexo=reunion.grupo.sexo).exclude(id=request.user.id)
                        for usr in usrs:
                            mb=usr.miembro
                            if not(mb in usr_recomendados) and not(mb in best_usr_recomendados):
                                usr_recomendados.append(mb)
                                nombre= mb.apellido +", "+mb.nombre
                                motivos=['Es un Usuario','Mismo Sexo que el grupo']
                                dic={'dni':mb.dni,'miembro': nombre, 'motivos':motivos}
                                data.append(dic)  
                    else:
                        print('weno esto si que ya es imposible china xd')   
        # if best_usr_recomendados:
        #     serializer=MiembroSerializer(best_usr_recomendados,many=True)
        # if (not(best_usr_recomendados) and usr_recomendados):
        #     serializer=MiembroSerializer(usr_recomendados,many=True)
        # if  (not(best_usr_recomendados and usr_recomendados) and mb_recomendados):
        #     serializer=MiembroSerializer(mb_recomendados,many=True)
        
        #print('data: ',data)
        return JSONResponse(data)

@csrf_exempt
def miembrosList(request):
    rn=request.GET.get('rn')
    print(rn)
    if request.method =='GET':
        reunion=Reunion.objects.get(nombre=rn)
        miembros=reunion.grupo.miembro.all()
        print(miembros)
        serializer=MiembroSerializer(miembros,many=True)
        result=dict()
        result = serializer.data
        return JSONResponse(result)

@csrf_exempt
def rolList(request):
    rol=request.GET.get('rol')
    print(rol)
    if request.method =='GET':
        rol=Rol.objects.get(id_rol=rol)
        miembros=CustomUser.objects.filter(rol_id=rol)
        print(miembros)
        serializer=UsuarioSerializer(miembros,many=True)
        result=dict()
        result = serializer.data
        return JSONResponse(result)
    
@csrf_exempt
def estadoList(request):
    usr= request.GET.get('usr')
    usuario = CustomUser.objects.get(id=usr)
    estado = Estado_Usuario.objects.filter(usuario_id=usuario.id).last()
    data=[]
    cant_r = Reunion.objects.filter(grupo__encargado=usuario.id,borrado=False)
    cant_r = len(list(cant_r))
    if usuario.is_active:
        if estado != None:
            print('usr ', usuario)
            print('estado ',estado)
            print('')
            fechona=estado.fecha.date()
            print('FECHONA: ',fechona)
            print('')
            if Encuesta.objects.filter(tipo_id=3,fecha_respuesta =fechona,miembro_id=usuario.miembro.dni).exists():
                encuesta = Encuesta.objects.filter(tipo_id=3,fecha_respuesta =fechona,miembro_id=usuario.miembro.dni)
                # encuesta = Encuesta.objects.get(id_encuesta=encuesta[0]['id_encuesta'])4
                print('-------------usr-------------- ', usuario)
                print('encuesta: ', encuesta)
                print('encuesta ',encuesta[0])
                link = '/sistema/verRespuesta/'+str(encuesta[0])
                #bueno ya tengo el link y el estado ahora tengo que contar cuantas reuniones tiene
                
                if estado.estado.estado == 'Critico' and estado.confirmado == True:
                    estado.estado.estado='Suspendido'
                dic = {'link':link,'estado':estado.estado.estado,'rn':cant_r}
            else:
                link=''
                dic = {'link':link,'estado':estado.estado.estado,'rn':cant_r}

        else:
            link=''
            estado="Muy Bueno"
            dic = {'link':link,'estado':estado,'rn':cant_r}
    else:
        if estado != None:
            fechona=estado.fecha.date()
            if Encuesta.objects.filter(tipo_id=3,fecha_respuesta =fechona,miembro_id=usuario.miembro.dni).exists():
                encuesta = Encuesta.objects.filter(tipo_id=3,fecha_respuesta =fechona,miembro_id=usuario.miembro.dni)
                link = '/sistema/verRespuesta/'+str(encuesta[0])
            else:
                link=''
        estado='Suspendido'
        dic = {'link':link,'estado':estado,'rn':cant_r}
    data.append(dic)
    print("-----------------------------//-----------------------")
    print('data: ',data)
    return JSONResponse(data)

@csrf_exempt
def reunionList(request):
    rn=request.GET.get('rn')
    if request.method =='GET':
        rn_base=Reunion.objects.get(nombre=rn) #no se si me va a dejar
        #vemos si hay una reunion posible para recomendar, osea aca ya entran las del mismo tipo
        encargado=rn_base.grupo.encargado
        print("")
        print('encargadito: ',encargado)
        print("")
        dic=[]
        data=[]
        motivos=[]
        i=0
        if Reunion.objects.filter(tipo_reunion=rn_base.tipo_reunion,borrado=False).exclude(grupo__encargado=encargado).exists():
            reuniones=Reunion.objects.filter(tipo_reunion=rn_base.tipo_reunion,borrado=False).exclude(grupo__encargado=encargado)
            print('')
            print('reunionesss: ',reuniones)
            print('')
            miembros=rn_base.grupo.miembro.all()
            for miembro in miembros:
                #print('miembro: ',miembro + 'base: ',rn_base.nombre)
                rn=[]
                ids=[]
                motivos=[]
                for reunion in reuniones:
                    print('reunion: ',reunion)
                    print('borrado: ',reunion.borrado)
                    if reunion.grupo.sexo== "Ambos" or reunion.grupo.sexo == miembro.sexo:
                        #print('esa reunion coincide con el sexo de la base')
                        hs_rn=reunion.horario
                        if Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta).exists():
                            horarios=Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta)
                            #aca yo traigo todos los horarios que coinciden con el de la reunion
                            for horario in horarios:
                                if Miembro.objects.filter(dni=miembro.dni,horario_disponible=horario).exists(): #aca veo si ese hs pertenece a un mb
                                    barrio=miembro.domicilio.barrio
                                    if barrio == reunion.domicilio.barrio:
                                        if not(reunion.nombre in rn):
                                            rn.append(reunion.nombre) #ESTA es la mejor reunion para recomendar
                                            ids.append(str(reunion.id_reunion))
                                            motivo='Coincide el Tipo de reunion, el sexo del grupo, el barrio y el horario disponible del miembro con el horario de la reunion'
                                            motivos.append(motivo)
                                            #dic={'motivos':motivos,'reunion': reunion.nombre, 'nombre':miembro.apellido + ', ' + miembro.nombre , 'id_reunion':str(reunion.id_reunion),'id_miembro':str(miembro.dni)} 
                                            #data.append(dic)
                                    else:
                                        if not(reunion.nombre in rn):
                                            rn.append(reunion.nombre) #Esta voy a ocupar si no es la mejor reunion
                                            ids.append(str(reunion.id_reunion))
                                            motivo='Coincide el Tipo de reunion, el sexo del grupo y el barrio'
                                            motivos.append(motivo)
                                            #esta reunion coincide con los horarios libres de las personas
                                else:
                                    if miembro.domicilio.barrio == reunion.domicilio.barrio:
                                        if not(reunion.nombre in rn):
                                            rn.append(reunion.nombre) #No coincide con los horarios libres pero si con la ubicacion
                                            ids.append(str(reunion.id_reunion))
                                            motivo='Coincide el Tipo de reunion, el sexo del grupo y el barrio'
                                            motivos.append(motivo)
                                    else: #bueno aca no hay en el mismo barrio ni en el mismo horario
                                        #tonces le pongo la reunion del mismo tipo al menos y genero
                                        if not(reunion.nombre in rn):
                                            rn.append(reunion.nombre)
                                            ids.append(str(reunion.id_reunion))
                                            motivo='Coincide el Tipo de reunion y el sexo del grupo'
                                            motivos.append(motivo)
                    else: #es del mismo tipo la rn
                        rn.append(reunion.nombre)
                        ids.append(str(reunion.id_reunion))
                        motivo='Coincide el Tipo de reunion'
                        motivos.append(motivo)
                #aca creo el dic con la lista de weas
                if len(motivos) == len(rn) :
                    print('coinciden las longitudes !')
                    print('Reuniones: ', rn)
                    print('motivos: ', motivos)
                    dic={'motivos':motivos,'reunion': rn, 'nombre':miembro.apellido + ', ' + miembro.nombre , 'id_reunion':ids,'id_miembro':str(miembro.dni)} 
                    data.append(dic)


            #aca estoy adentro del for de mb

        #weno no tiene chiste que vuelva a recorrer todo de nuevo pero bueno no me manejo bien con arrays
        #dic = {'reunion': change.field, 'nombre':change.old, 'id_reunion':change.new}

        if not(data):   
            data = {
                'is_taken': True
            }
            if data['is_taken']:
                data['error_message']  = 'No hay Reunion Recomendada'
            #print(data)
            return JsonResponse(data)
        else:
            #serializer=ReunionSerializer(rn_recomendada,many=True)
            #result=dict()
            #result = serializer.data
            print(data)
            return JSONResponse(data)

def filtros_estado_miembro(request):
    desde = request.GET['desde']
    hasta = request.GET['hasta']
    usr = request.GET['usr']
    print('')
    print('USUARIO: ',usr)
    print('')
    cant_mb=0 #cantidad de estados muy buenos
    cant_b=0  #cantidad de estados buenos
    cant_m=0  #cantidad de estados medios
    cant_c=0  #cantidad de estados criticos

    #Me aseguro de tener los datos que eligió y aplico los filtros
    if request.GET['desde'] == '' and request.GET['hasta'] =='': #si no eligio nada weno le muestro todos los actuales
        if usr=="":
            usuarios= CustomUser.objects.filter(is_active=True)
            cant_total=len(list(usuarios))
            for usuario in usuarios:
                estado = Estado_Usuario.objects.filter(usuario_id=usuario.id).order_by('-fecha').first() #orden descendente
                #en mi mente trae del mas actual al mas viejo, descienden las fechas
                #tengo que comprobar
                if estado != None:
                        if estado.estado.id == 1:
                            cant_mb += 1
                        if estado.estado.id == 2:
                            cant_b += 1
                        if estado.estado.id == 3:
                            cant_m += 1
                        if estado.estado.id == 4 : 
                            cant_c += 1
                else: #si nunca registro un estado es porque esta mb, nunca falto consecutivamente ni nada
                    cant_mb += 1 
            #bien ahora porcentajes
        else:
            usuario= CustomUser.objects.get(username=usr)
            estados = Estado_Usuario.objects.filter(usuario_id=usuario.id) #traigo todos! :o
            print('estados: ',estados)
            cant_total = len(estados)
            if len(estados) != 0: #creo que es un queryset vacio xD
                for estado in estados:
                    if estado.estado.id == 1:
                        cant_mb += 1
                    if estado.estado.id == 2:
                        cant_b += 1
                    if estado.estado.id == 3:
                        cant_m += 1
                    if estado.estado.id == 4 : 
                        cant_c += 1
            else: #si nunca registro un estado es porque esta mb, nunca falto consecutivamente ni nada
                print('aca asigno la wea')
                cant_mb += 1
                cant_total=1
                 
            #bien ahora porcentajes
            
    else: #es porque hay un desde y/o un hasta
        if request.GET['desde'] != '' and request.GET['hasta'] !='':
            if usr == "":
                #castear hasta pa que sea un timedate
                new_h = datetime.datetime.strptime(hasta, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                usuarios= CustomUser.objects.filter(date_joined__lte=new_h) #traigo todos los usr que estaban creados antes de la fecha max (hasta)
                cant_total=len(list(usuarios))
                desde=datetime.datetime.strptime(desde, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                hasta=datetime.datetime.strptime(hasta, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                for usuario in usuarios:
                    estado= Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__range=(desde,hasta)).order_by('-fecha').first()
                    if estado != None:
                        if estado.estado.id == 1:
                            cant_mb += 1
                        if estado.estado.id == 2:
                            cant_b += 1
                        if estado.estado.id == 3:
                            cant_m += 1
                        if estado.estado.id == 4 : 
                            cant_c += 1
                    else: #si no registro un estado en ese rango voy a ver el ultimo estado que tenia
                        estado = Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__lte=desde).order_by('-fecha').first()
                        if estado != None:
                            if estado.estado.id == 4: 
                                cant_c += 1
                            else:
                                cant_mb+=1 #osea si no esta suspendido ni nada entonces ta mb
                        else:
                            cant_mb+=1 #osea no registro nada antes que la fecha desde, estaba mb
            else:
                usuario= CustomUser.objects.get(username=usr) 
                desde=datetime.datetime.strptime(desde, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                hasta=datetime.datetime.strptime(hasta, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                estados= Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__range=(desde,hasta))
                cant_total=len(estados)
                if len(estados) != 0:
                    for estado in estados:
                        if estado.estado.id == 1:
                            cant_mb += 1
                        if estado.estado.id == 2:
                            cant_b += 1
                        if estado.estado.id == 3:
                            cant_m += 1
                        if estado.estado.id == 4 : 
                            cant_c += 1
                else: #si no registro un estado en ese rango voy a ver el ultimo estado que tenia
                    estado = Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__lte=desde).order_by('-fecha').first()
                    if estado != None:
                        if estado.estado.id == 4: 
                            cant_c += 1
                        else:
                            cant_mb+=1 #osea si no esta suspendido ni nada entonces ta mb
                    else:
                        cant_mb+=1 #osea no registro nada antes que la fecha desde, estaba mb
                    cant_total=1
        else: #Weno ahora tengo que ver cual de las 2 estan vacias
            if desde !='':
                if usr=="":
                    desde=datetime.datetime.strptime(desde, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                    usuarios= CustomUser.objects.all() #traigo todos los usr
                    cant_total=len(list(usuarios))
                    for usuario in usuarios:
                        estado= Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__gte=desde).order_by('-fecha').first()
                        #traigo un estado por miembro, el mas actual
                        if estado != None:
                            if estado.estado.id == 1:
                                cant_mb += 1
                            if estado.estado.id == 2:
                                cant_b += 1
                            if estado.estado.id == 3:
                                cant_m += 1
                            if estado.estado.id == 4 : 
                                cant_c += 1
                        else: #si no registro un estado en ese rango voy a ver el ultimo estado que tenia
                            estado = Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__lte=desde).order_by('-fecha').first()
                            if estado != None:
                                if estado.estado.id == 4 : 
                                    cant_c += 1
                                else:
                                    cant_mb+=1 #osea si no esta suspendido ni nada entonces ta mb
                            else:
                                cant_mb+=1 #osea no registro nada antes que la fecha desde, estaba mb
                else:
                    desde=datetime.datetime.strptime(desde, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                    usuario= CustomUser.objects.get(username=usr) #traigo todos los usr
                    estados= Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__gte=desde).order_by('-fecha')
                    #traigo todos los estados del usuario a partir de esa fecha
                    if len(estados) != 0:
                        for estado in estados:
                            if estado.estado.id == 1:
                                cant_mb += 1
                            if estado.estado.id == 2:
                                cant_b += 1
                            if estado.estado.id == 3:
                                cant_m += 1
                            if estado.estado.id == 4 : 
                                cant_c += 1
                    else: #si no registro un estado en ese rango voy a ver el ultimo estado que tenia
                        estado = Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__lte=desde).order_by('-fecha').first()
                        if estado != None:
                            if estado.estado.id == 4 : 
                                cant_c += 1
                            else:
                                cant_mb+=1 #osea si no esta suspendido ni nada entonces ta mb
                        else:
                            cant_mb+=1 #osea no registro nada antes que la fecha desde, estaba mb
                        cant_total = 1
            else:
                #castear hasta pa que sea un timedate
                if usr=="":
                    new_h = datetime.datetime.strptime(hasta, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                    usuarios= CustomUser.objects.filter(date_joined__lte=new_h) #traigo todos los usr que estaban creados antes de la fecha max (hasta)
                    cant_total=len(list(usuarios))
                    hasta=datetime.datetime.strptime(hasta, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                    for usuario in usuarios:
                        estado= Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__lte=hasta).order_by('-fecha').first()
                        if estado != None:
                            if estado.estado.id == 1:
                                cant_mb += 1
                            if estado.estado.id == 2:
                                cant_b += 1
                            if estado.estado.id == 3:
                                cant_m += 1
                            if estado.estado.id == 4 : 
                                cant_c += 1
                        else: 
                            cant_mb+=1 #osea no registro nada antes que la fecha desde, estaba mb
                else:
                    usuario=CustomUser.objects.get(username=usr)
                    hasta=datetime.datetime.strptime(hasta, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
                    estados= Estado_Usuario.objects.filter(usuario_id=usuario.id,fecha__lte=hasta).order_by('-fecha')
                    cant_total = len(estados)
                    if len(estados) != 0:
                        for estado in estados:
                            if estado.estado.id == 1:
                                cant_mb += 1
                            if estado.estado.id == 2:
                                cant_b += 1
                            if estado.estado.id == 3:
                                cant_m += 1
                            if estado.estado.id == 4 : 
                                cant_c += 1
                    else: 
                        cant_mb+=1 #osea no registro nada antes que la fecha desde, estaba mb
                        cant_total = 1


    if cant_total == 0:
        #data = [0,0,0,0]
        print('errorcito')
    else:
        cant_mb = (cant_mb * 100) / cant_total
        cant_b = (cant_b * 100) / cant_total
        cant_m = (cant_m * 100) / cant_total
        cant_c = (cant_c * 100) / cant_total
        
        data = [round(cant_mb, 2),round(cant_b, 2),round(cant_m, 2),round(cant_c, 2)]
    print("-----------------------------//-----------------------")
    print('data: ',data)
    return JSONResponse(data)

def filtros_estado_reunion(request):
    desde = request.GET['desde']
    hasta = request.GET['hasta']
    rn = request.GET['rn']
    print('desde ',desde)
    print('hasta ',hasta)
    cant_mb=0 #cantidad de estados muy buenos
    cant_b=0  #cantidad de estados buenos
    cant_m=0  #cantidad de estados medios
    cant_c=0  #cantidad de estados criticos
    cant_s=0  #cantidad de miembros que no respondieron
    cant_total=0
    #lo primero y mas importante tiene que seleccionar una reunion
    if rn != '': #siemre va ser distinto de vacio no le doy otra chance
        if request.GET['desde'] == '' and request.GET['hasta'] =='': #si ambos son vacios muestro los actuales
            #bueno primero tengo que ver cual fue la ultima encuesta que le mande a esa reunion
            enc = Encuesta.objects.filter(reunion_id = rn, tipo_id = 2).last()
            #en teoria eso es orden descendente por eso obtengo el primero
            if enc != None:
                fecha=enc.fecha_envio
                print('fechona ',fecha)
                encuestas = Encuesta.objects.filter(reunion_id=rn,tipo=2,fecha_envio=fecha).exclude(fecha_respuesta=None)#ahora obtengo todas las enviadas en esa fecha
                print(encuestas)
                cant_total=len(list(encuestas)) #cantidad de encuestas enviadas a esa rn en esa fecha
                cant_s = Encuesta.objects.filter(reunion=rn, tipo=2,fecha_respuesta=None)
                cant_s = len(list(cant_s))
                cant_total += cant_s
                print('------------------')
                print('cantidad sin responder ', cant_s)
                print('cantidad total ', cant_total)
                print('------------------')
                for encuesta in encuestas:
                    print('id_e: ',encuesta.id_encuesta)
                    print("rn, ",rn)
                    estado= Estado_Reunion.objects.get(encuesta_id=encuesta.id_encuesta,reunion_id=rn)
                    print('estado: ',estado)
                    if estado.estado_id == 1:
                        cant_mb += 1
                    if estado.estado_id == 2:
                        cant_b += 1
                    if estado.estado_id == 3:
                        cant_m += 1
                    if estado.estado_id == 4:
                        cant_c += 1

        else: #es porque hay un desde y/o un hasta
            if request.GET['desde'] != '' and request.GET['hasta'] !='':
                #traigo todas las encuestas que fueron enviadas entre esas fechas
                encuestas = Encuesta.objects.filter(reunion_id=rn,tipo=2,fecha_envio__range=(desde,hasta)).exclude(fecha_respuesta=None)
                cant_total=len(list(encuestas)) #cantidad de encuestas enviadas a esa rn en ese rango de fechas
                cant_s = Encuesta.objects.filter(reunion=rn, tipo=2,fecha_respuesta=None,fecha_envio__range=(desde,hasta))
                cant_s = len(list(cant_s)) #cantidad de encuestas enviadas a esa rn en ese rango de fechas y sin respuestas
                cant_total += cant_s
                print('------------------')
                print('cantidad sin responder ', cant_s)
                print('cantidad total ', cant_total)
                print('------------------')
                for encuesta in encuestas:
                    print('encuesta: ',encuesta.id_encuesta)
                    if Estado_Reunion.objects.filter(encuesta_id=encuesta.id_encuesta,reunion_id=rn).exists():
                        estado= Estado_Reunion.objects.get(encuesta_id=encuesta.id_encuesta,reunion_id=rn)
                        print('estado: ',estado)
                        if estado.estado_id == 1:
                            cant_mb += 1
                        if estado.estado_id == 2:
                            cant_b += 1
                        if estado.estado_id == 3:
                            cant_m += 1
                        if estado.estado_id == 4:
                            cant_c += 1
            else:
                if request.GET['desde'] != '':
                    print('DESDE NO ESTABA VACIO')
                    #traigo todas las encuestas que fueron enviadas entre esas fechas
                    encuestas = Encuesta.objects.filter(reunion_id=rn,tipo=2,fecha_envio__gte=desde).exclude(fecha_respuesta=None)
                    cant_total=len(list(encuestas)) #cantidad de encuestas enviadas desde esa fecha en adelate
                    cant_s = Encuesta.objects.filter(reunion=rn, tipo=2,fecha_respuesta=None,fecha_envio__gte=desde)
                    cant_s = len(list(cant_s)) #cantidad de encuestas enviadas a esa rn a desde esa fecha en adelante y sin respuestas
                    cant_total += cant_s
                    print('------------------')
                    print('cantidad sin responder ', cant_s)
                    print('cantidad total ', cant_total)
                    print('------------------')
                    for encuesta in encuestas:
                        print('encuesta: ',encuesta.id_encuesta)
                        if Estado_Reunion.objects.filter(encuesta_id=encuesta.id_encuesta,reunion_id=rn).exists():
                            estado= Estado_Reunion.objects.get(encuesta_id=encuesta.id_encuesta,reunion_id=rn)
                            print('estado: ',estado)
                            if estado.estado_id == 1:
                                cant_mb += 1
                            if estado.estado_id == 2:
                                cant_b += 1
                            if estado.estado_id == 3:
                                cant_m += 1
                            if estado.estado_id == 4:
                                cant_c += 1
                else:
                    #traigo todas las encuestas que fueron hasta esa fecha
                    print('ACA TENGO QUE ENTRAR')
                    encuestas = Encuesta.objects.filter(reunion_id=rn,tipo=2,fecha_envio__lte=hasta).exclude(fecha_respuesta=None)
                    cant_total=len(list(encuestas)) #cantidad de encuestas enviadas hasta esa fecha
                    cant_s = Encuesta.objects.filter(reunion=rn, tipo=2,fecha_respuesta=None,fecha_envio__lte=hasta)
                    cant_s = len(list(cant_s)) #cantidad de encuestas enviadas a esa rn a hasta esa fecha y sin respuestas
                    cant_total += cant_s
                    print('------------------')
                    print('cantidad sin responder ', cant_s)
                    print('cantidad total ', cant_total)
                    print('------------------')
                    for encuesta in encuestas:
                        print('encuesta: ',encuesta.id_encuesta)
                        if Estado_Reunion.objects.filter(encuesta_id=encuesta.id_encuesta,reunion_id=rn).exists():
                            estado= Estado_Reunion.objects.get(encuesta_id=encuesta.id_encuesta,reunion_id=rn)
                            print('estado: ',estado)
                            if estado.estado_id == 1:
                                cant_mb += 1
                            if estado.estado_id == 2:
                                cant_b += 1
                            if estado.estado_id == 3:
                                cant_m += 1
                            if estado.estado_id == 4:
                                cant_c += 1


        #bien ahora porcentajes
        data = []
        if cant_total != 0:
            cant_mb = (cant_mb * 100) / cant_total
            cant_b = (cant_b * 100) / cant_total
            cant_m = (cant_m * 100) / cant_total
            cant_c = (cant_c * 100) / cant_total
            cant_s = (cant_s * 100) / cant_total
            data = [round(cant_mb, 2),round(cant_b, 2),round(cant_m, 2),round(cant_c, 2),round(cant_s,2)]
            print('datitos bn en teoria ', data)
        else:
            print('entre mal cabeza')
            data = []
            #ver de poner un mensajito
    print("-----------------------------//-----------------------")
    print('data: ',data)
    return JSONResponse(data)

def filtros_asistencias(request):
    desde = request.GET['desde']
    hasta = request.GET['hasta']
    mb = request.GET['mb']
    rn = request.GET['rn']
    rol = request.GET['rol']
    if Reunion.objects.filter(nombre=rn).exists():
        reunion= Reunion.objects.get(nombre=rn) 
        rn = reunion.id_reunion
    else:
        rn=''
    print('REUNION ', rn)
    print('MIEMBRO ',mb)
    print('ROL: ',rol)
    cant_ast=0 #cantidad de faltas
    cant_fal=0
    cant_total=0   
    if request.GET['desde'] == '' and request.GET['hasta'] =='': #si ambos son vacios muestro los actuales
        if rn != '': #weno si no hay limite de fecha y rn esta seleccionado
            #bueno voy a traer todos los registros de asistencias de esa rn
            cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True)
            cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False)
            cant_ast= len(list(cant_ast))
            cant_fal= len(list(cant_fal))
            cant_total = cant_ast + cant_fal
        if (not(rn != '') and mb != 'null'):
            cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True)
            cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False)
            cant_ast= len(list(cant_ast))
            cant_fal= len(list(cant_fal))
            cant_total = cant_ast + cant_fal
        if rol != 'null':
            print('')
            usuarios = CustomUser.objects.filter(rol_id=int(rol))
            print('usuarios ',usuarios)
            print('')
            for usuario in usuarios:
                miembro = usuario.miembro
                cant_asti = Asistencia.objects.filter(miembro_id=miembro.dni,presente=True)
                cant_falt= Asistencia.objects.filter(miembro_id=miembro.dni,presente=False)
                cant_ast += len(list(cant_asti))
                cant_fal += len(list(cant_falt))
                cant_total += cant_ast + cant_fal
                print(cant_total)
    else: #weno si puso horarios tengo que ver cual
        if request.GET['desde'] != '' and request.GET['hasta'] !='':
            if rn != '': #Bueno si quiere filtar las asitencias de la reunion rn entre esas fechas entonces
                #bueno voy a traer todos los registros de asistencias de esa rn
                cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True,fecha__range=(desde,hasta))
                cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False,fecha__range=(desde,hasta))
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal

            if (not(rn != '') and mb != 'null'):
                cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True,fecha__range=(desde,hasta))
                cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False,fecha__range=(desde,hasta))
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal

            if rol != 'null': 
                print('')
                print('entre en el rol')
                usuarios = CustomUser.objects.filter(rol_id=rol)
                for usuario in usuarios:
                    miembro = usuario.miembro
                    cant_ast = Asistencia.objects.filter(miembro_id=miembro.dni,presente=True,fecha__range=(desde,hasta))
                    cant_fal= Asistencia.objects.filter(miembro_id=miembro.dni,presente=False,fecha__range=(desde,hasta))
                    cant_ast= len(list(cant_ast))
                    cant_fal= len(list(cant_fal))
                    cant_total = cant_ast + cant_fal
        else:
            if request.GET['desde'] != '': #si entra aca es porque uno de los dos esta vacio, hay que ver cual
                #en este caso cargo solo el desde
                if rn != '': #Bueno si quiere filtar las asitencias de la reunion rn desde esa fecha en adelante
                    #bueno voy a traer todos los registros de asistencias de esa rn
                    print('entre en 1')
                    print('desde ',desde)
                    print('rn ',rn)
                    cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True,fecha__gte=desde)
                    print('ast ', cant_ast)
                    cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False,fecha__gte=desde)
                    cant_ast= len(list(cant_ast))
                    print('ast ', cant_ast)
                    cant_fal= len(list(cant_fal))
                    print('cant_f ',cant_fal)
                    cant_total = cant_ast + cant_fal

                if (not(rn != '') and mb != 'null'):
                    print('entre en 2')
                    cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True,fecha__gte=desde)
                    cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False,fecha__gte=desde)
                    cant_ast= len(list(cant_ast))
                    cant_fal= len(list(cant_fal))
                    cant_total = cant_ast + cant_fal
                else:
                    if rol != 'null': 
                        print('entre en 3')
                        usuarios = CustomUser.objects.filter(rol_id=rol)
                        for usuario in usuarios:
                            miembro = usuario.miembro
                            cant_ast = Asistencia.objects.filter(miembro_id=miembro.dni,presente=True,fecha__gte=desde)
                            cant_fal= Asistencia.objects.filter(miembro_id=miembro.dni,presente=False,fecha__gte=desde)
                            cant_ast= len(list(cant_ast))
                            cant_fal= len(list(cant_fal))
                            cant_total = cant_ast + cant_fal
            else:
                if request.GET['hasta'] != '': #en realidad con un else ya anda pero por la dudas
                    if rn != '': #Bueno si quiere filtar las asitencias de la reunion rn desde esa fecha limita hacia atras
                        #bueno voy a traer todos los registros de asistencias de esa rn
                        cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True,fecha__lte=hasta)
                        cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False,fecha__lte=hasta)
                        cant_ast= len(list(cant_ast))
                        cant_fal= len(list(cant_fal))
                        cant_total = cant_ast + cant_fal

                    if (not(rn != '') and mb != 'null'):
                        cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True,fecha__lte=hasta)
                        cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False,fecha__lte=hasta)
                        cant_ast= len(list(cant_ast))
                        cant_fal= len(list(cant_fal))
                        cant_total = cant_ast + cant_fal
                    else:
                        if rol != 'null': 
                            usuarios = CustomUser.objects.filter(rol_id=rol)
                            for usuario in usuarios:
                                miembro = usuario.miembro
                                cant_ast = Asistencia.objects.filter(miembro_id=miembro.dni,presente=True,fecha__lte=hasta)
                                cant_fal= Asistencia.objects.filter(miembro_id=miembro.dni,presente=False,fecha__lte=hasta)
                                cant_ast= len(list(cant_ast))
                                cant_fal= len(list(cant_fal))
                                cant_total = cant_ast + cant_fal
                
        
    data = []
    if cant_total != 0: #no tenian ninguna asitencia
        cant_ast = (cant_ast * 100) / cant_total
        cant_fal = (cant_fal * 100) / cant_total
        data = [round(cant_ast,2),round(cant_fal,2)]
        
            
            #ver de poner un mensajito
    print("-----------------------------//-----------------------")
    print('data: ',data)
    return JSONResponse(data)

def Calendario(request):
    #Weno la idea es recuperar las asistencias de todas las reuniones, todas todas
    #lo primero es traer las reuniones
    reuniones = Reunion.objects.all()
    #por cada reunion voy a ver las asistencias
    data=[]
    for reunion in reuniones:
        #traigo todas las asistencias que tuvo esa reunion
        #tendria que ver las fechas ahora
        #print("--------------------------------------------"+reunion.nombre)
        #print("consulta: ", Asistencia.objects.values("fecha").filter(reunion=reunion,presente=False).annotate(count=Count("fecha")))
        #se como traer los presentes y ausentes de cada fecha de cada reunion
        registros_f= Asistencia.objects.values("fecha").filter(reunion=reunion,presente=False).annotate(count=Count("fecha"))
        registros_a= Asistencia.objects.values("fecha").filter(reunion=reunion,presente=True).annotate(count=Count("fecha"))
        color_rn = color()
        #print('Reunion, color ',reunion, color_rn)
        for registro in registros_a: #por cada registro de asistencias (fechas agrupadas)
            #print("")
            #print('registro.fechona: ', registro.get('fecha'))
            #print("")
            cant_a=0 #cantidad de presentes
            cant_f =0 #cantidad de faltantantes
            fecha=registro['fecha']
            #print(' ta o no ', registros_f.get(fecha=fecha))
            try:
                if registros_f.get(fecha=fecha): #si esa fecha esta en las faltas obtengo ese reg
                    reg = registros_f.get(fecha=fecha)
                    cant_f = reg['count']
            except:
                print("Oops!  no hay registros")

            cant_a = registro['count']
            dic = {'reunion':reunion.nombre,'fecha':fecha,'cant_a':cant_a,'cant_f':cant_f,'color':color_rn}
            data.append(dic)
        for registro in registros_f:
            cant_a=0 #cantidad de presentes
            cant_f =0 #cantidad de faltantantes
            fecha=registro['fecha'] 
            #print('fecha ',fecha)
            try:
                if registros_a.get(fecha=fecha): #si esa fecha esta en las ast, entonces y cargue
                    print('ya ta')
            except:
                #print('faltaron todos ', reunion.nombre)
                #print('fecha, ', fecha)
                cant_f = registro['count']
                dic = {'reunion':reunion.nombre,'fecha':fecha,'cant_a':cant_a,'cant_f':cant_f,'color':"#F78181"}
                data.append(dic)
        
    #print("-----------------------------//-----------------------")
    #print('data: ',data)
    return JSONResponse(data)
