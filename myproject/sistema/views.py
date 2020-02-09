from django.shortcuts import render,redirect
from .forms import *
from .models import *
from mensajeria.models import *
from mensajeria.views import *
from datetime import date
import datetime
from usuario.models import *
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


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def days_between(d1, d2):
    return abs(d2 - d1).days
    
@login_required
def Home(request):
    #Tengo que ver de recuperar el ultimo registro de asistencia por reunion, si pasaron mas de 7 dias 
    #y no hubo un registro, ponerle falta al encargado
    usuario = request.user
    usuarios = CustomUser.objects.all()
    miembro = Miembro.objects.get(dni=usuario.miembro_id)
    if miembro.sexo=="Femenino":
        sexo="Femenino"
    else:
        sexo="Masculino"
    context ={'usuario':usuario,'sexo':sexo,'usuarios':usuarios}
    miembros=[]
    miembros.append(str(miembro.dni))
    # asunto="Wenas"
    # mensaje=" Gracias lina! entra aca -> http://localhost:8000/Home"
    # enviarMail(miembros,asunto,mensaje)
    #tengo que ver si el usr no tiene una falta que no ingreso para eso
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
        #ahora que le puse la falta es el momento de contar cuantas faltas CONSECUTIVAS TIENE
        consulta=Asistencia.objects.filter(miembro=miembro,justificado=False,reunion=reunion.id_reunion).order_by('fecha')[:cant]
        cantidad = len (list(consulta)) #paso la cantidad de registros de faltas que encontro a cantidad
        if cantidad >= cant: #si la cantidad es >= al numero admisible de consecutivas entonces le creo una encuesta pendiente
            encuesta= Encuesta()
            encuesta.tipo=Tipo_Encuesta.objects.get(id_tipo_encuesta=3)
            encuesta.miembro=miembro
            encuesta.fecha_envio=date.today()
            encuesta.respondio=False
            encuesta.reunion=reunion
            encuesta.save()
            return redirect('/sistema/agregarRespuesta')

    if Asistencia.objects.filter(miembro=miembro,justificado=False).exists():
        #tiene que haber un counter lo necesito para elegir el tipo xd
        #aca tengo que contar cuantas faltas tiene por ahora es cada 1 y poner la reunion jiji
        encuesta= Encuesta()
        encuesta.borrado=False #ver si realmente puedo borrar una encuesta xd creeria que no se debe
        encuesta.tipo=Tipo_Encuesta.objects.get(id_tipo_encuesta=1)
        encuesta.miembro=miembro
        encuesta.fecha_envio=date.today()
        encuesta.respondio=False
        ast=Asistencia.objects.filter(miembro=miembro,justificado=False).last()
        encuesta.reunion=ast.reunion
        encuesta.save() #Esto quiere decir que tenia una falta no mas
        #aca deberia notificarle o algo, de que tiene una encuesta pendiente
        #return redirect('agregarRespuesta') asi estaba antes

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
    else:
        print('weno alguien tiene que empezar no?')
    return render(request,'sistema/index.html',context)

def estadistica_miembro(request):
    if request.method=='POST':
        print('y cuando va a hacer post linarda xD')
    else:
        
        return render(request,'sistema/estadistica_miembro.html')

def estadistica_reunion(request):
    reuniones = Reunion.objects.all()
    return render(request,'sistema/estadistica_reunion.html',{'reuniones':reuniones})

def estadistica_asistencias(request):
    reuniones = Reunion.objects.all()
    miembros = Miembro.objects.all()
    roles = Rol.objects.all()
    return render(request,'sistema/estadistica_asistencias.html',{'reuniones':reuniones,'miembros':miembros,'roles':roles})

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
        grupo=grupo_form.save(commit=False)
        grupo.encargado=request.POST.get('encargado')
        grupo.changeReason ='Creacion'
        grupo.save()
        grupo.miembro.set(request.POST.getlist('miembro'))
        grupo.save()
        return redirect('/sistema/listarGrupo')
    else:
        usuarios=CustomUser.objects.all()
        grupo_form=GrupoForm()
    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form,'miembros':miembros,'usuarios':usuarios})

def listarGrupo(request):
    grupos = Grupo.objects.filter(borrado=False)
    return render(request,'sistema/listarGrupo.html',{'grupos':grupos})

def validarGrupo(request):
    nombre = request.GET.get('nombre')
    data = {
        'is_taken': Grupo.objects.filter(nombre=nombre).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Este nombre de grupo ya existe, por favor elige otro nombre'
    print(data)
    return JsonResponse(data)

def editarGrupo(request,id_grupo):
    grupo = Grupo.objects.get(id_grupo=id_grupo)
    if request.method =='GET':
        grupo_form=GrupoForm(instance=grupo)
    else:
        grupo_form=GrupoForm(request.POST,instance=grupo)
        if grupo_form.is_valid():
            grupo=grupo_form.save(commit=False)
            grupo.changeReason='Modificacion'
            grupo.save()
        return redirect('/sistema/listarGrupo')
    return render(request,'sistema/crearGrupo.html',{'grupo_form':grupo_form})

def eliminarGrupo(request,id_grupo):
    grupo = Grupo.objects.get(id_grupo=id_grupo)
    grupo.borrado=True
    grupo.changeReason='Eliminacion'
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
        if 'btn-add-provincia' in request.POST:
            provincia=request.POST.get('prov',None)
            provincia=provincia.capitalize()
            if Provincia.objects.filter(provincia=provincia).exists():
                print('nombre repetido china')#vo tenes que cambiar esto michinita
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
            estado_civil_form=request.POST.get('estado_civil')
            domicilio_form=DomicilioForm(request.POST)
            horario_form=Horario_DisponibleForm(request.POST)
            if not(miembro_form.is_valid() and horario_form.is_valid() and barrio_form!=None and domicilio_form.is_valid()):
                messages.error(request, 'Debe completar todos los campos obligatorios')
                return redirect('/sistema/crearMiembro')
            
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

                return redirect('/sistema/listarMiembro')
        

    return render(request,'sistema/editarMiembro.html',{'localidad_form':localidad_form,'barrio_form':barrio_form,'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form,'horario_form':horario_form})

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
                tipo_reunion=tipo_reunion_form.save(commit=False)
                tipo_reunion.changeReason="Creacion"
                tipo_reunion.save()
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
            tipo_reunion=tipo_reunion_form.save(commit=False)
            tipo_reunion.changeReason="Modificacion"
            tipo_reunion.save()
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
        tipo_reunion.changeReason="Eliminacion"
        tipo_reunion.save()
    return redirect('/sistema/listarTipo_Reunion/')

def crearReunion(request):
    if request.method == 'POST':
        reunion_form=ReunionForm(request.POST)
        domicilio_form=DomicilioForm(request.POST)
        horario_form= Horario_DisponibleForm(request.POST)

        if reunion_form.is_valid()and domicilio_form.is_valid():
            if Reunion.objects.filter(nombre=nombrecito).exists():
                messages.error(request, 'Nombre no disponible')
            else:
                horario=horario_form.save(commit=False)
                horario.save()
                reunion=reunion_form.save(commit=False)
                domicilio=domicilio_form.save(commit=False)
                domicilio.save()
                reunion.changeReason ='Creacion'
                reunion.domicilio=domicilio
                reunion.horario=horario
                reunion.save()
                return redirect('/sistema/listarReunion')
    else:
        localidad_form=LocalidadForm()
        barrio_form=BarrioForm()
        reunion_form=ReunionForm()
        domicilio_form=DomicilioForm()
        horario_form=Horario_DisponibleForm()
    return render(request,'sistema/editarReunion.html',{'barrio_form':barrio_form,'localidad_form':localidad_form,'horario_form':horario_form,'reunion_form':reunion_form,'domicilio_form':domicilio_form})

def editarReunion(request,id_reunion):
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
        domicilio_form=DomicilioForm(instance = domicilio)
        print(reunion_form.errors.as_data())
        if reunion_form.is_valid():
            domicilio.save()
            reunion.changeReason ='Modificacion'
            reunion.save()
            return redirect('/sistema/listarReunion')
    return render(request,'sistema/editarReunion.html',{'barrio_form':barrio_form,'localidad_form':localidad_form,'horario_form':horario_form,'reunion_form':reunion_form,'domicilio_form':domicilio_form})

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
                asistencia = Asistencia.objects.get(miembro_id = check,fecha=fecha)
                asistencia.presente=True
                justificado=True
                asistencia.changeReason="Creacion"
                asistencia.save()
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
    return render(request,'sistema/verAsistencia.html',{'asistencia':asistencia,'reunion':reunion})

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
                    mensaje=Mensaje.objects.get(id=4)
                    asunto=mensaje.tipo
                    mensaje=mensaje.mensaje
                    enviarWhatsapp(mensaje,miembros)
                    mensaje=mensaje + ' ->  http://localhost:8000/sistema/agregarRespuestaReunion/'+str(encuesta.id_encuesta)
                    enviarMail(miembros,asunto,mensaje)
                    miembros=[]#limpio porque voy a enviar 1 por uno
        return redirect('home')
    else:
        pregunta=Pregunta.objects.filter(borrado=False)
        tipo_encuesta=Tipo_Encuesta.objects.all()
        reuniones=Reunion.objects.filter(borrado=False)
        return render(request,'sistema/agregarEncuesta.html',{'tipo_encuesta':tipo_encuesta,'pregunta':pregunta,'reuniones':reuniones})

def agregarPregunta(request):
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
        return redirect('home')
    else:
        pregunta_form=PreguntaForm()
        tipos=Tipo_Pregunta.objects.all()
    return render(request,'sistema/agregarPregunta.html',{'pregunta_form':pregunta_form,'tipos':tipos})

def validarPregunta(request):
    nombre = request.GET.get('nombre')
    data = {
        'is_taken': Pregunta.objects.filter(descripcion=nombre).exists()
    }
    if data['is_taken']:
        data['error_message']  = 'Esta Pregunta ya existe, por favor haz otra pregunta'
    print(data)
    return JsonResponse(data)

def eliminarPregunta(request,id_pregunta):
    pregunta=Pregunta.objects.get(id_pregunta=id_pregunta)
    opciones=Opciones.objects.filter(pregunta_id=id_pregunta)
    for opcion in opciones:
        opcion.borrado=True
        opcion.save()
    pregunta.borrado=True
    pregunta.save()
    return redirect('home')

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
        return redirect('home')
    if request.method == 'POST':
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
                estado=Estado(usuario=request.user,estado="Pendiente",confirmado=False)
                estado.save()
                #aca pum ya notifico
            if puntos <= puntos_total/2 and puntos > puntos_total/4:
                print("Medio")
                estado=Estado(usuario=request.user,estado="Medio")
                estado.save()
            if (puntos > puntos_total/2) and (puntos <= (puntos_total-(puntos_total/4))):
                print("Bueno")
                estado=Estado(usuario=request.user,estado="Bueno")
                estado.save()
                mensaje=Mensaje.objects.get(id=1)
                mensaje=mensaje.id
                miembros=[]
                miembros.append(str(request.user.miembro.dni))
                enviarWhatsapp(mensaje,miembros)


            if (puntos > (puntos_total-(puntos_total/4))) and (puntos <= puntos_total):
                print('Re bien!!')
                estado=Estado(usuario=request.user,estado="Muy Bueno")
                estado.save()
            
            return redirect('home')

    return render(request,'sistema/agregarRespuesta.html',{'preguntas':preguntas,'reunion':reunion})

def agregarRespuestaReunion(request,id_encuesta):  
    encuesta=Encuesta.objects.get(id_encuesta=id_encuesta)
    preguntas=encuesta.tipo.preguntas.filter(borrado=False)
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
            #tengo que crear ese estado critico y que quede en la espera de confirmacion
            #para la baja
            estado=Estado_Reunion(estado="Critico",reunion=reunion)
            estado.save()
            #aca pum ya notifico
        if puntos <= puntos_total/2 and puntos > puntos_total/4:
            print("medio")
            estado=Estado_Reunion(estado="Medio",reunion=reunion)
            estado.save()
        if (puntos > puntos_total/2) and (puntos <= (puntos_total-(puntos_total/4))):
            print("Bueno")
            estado=Estado_Reunion(estado="Bueno",reunion=reunion)
            estado.save()
        if (puntos > (puntos_total-(puntos_total/4))) and (puntos <= puntos_total):
            print('Re bien!!')
            estado=Estado_Reunion(estado="Muy Bueno",reunion=reunion)
            estado.save()
        return redirect('home')    

    return render(request,'sistema/agregarRespuesta.html',{'preguntas':preguntas,'reunion':reunion})

def verRespuesta(request,id_encuesta):
    encuesta=Encuesta.objects.get(id_encuesta=id_encuesta)
    respuestas=Respuesta.objects.filter(encuesta=encuesta)
    if request.method =='POST':
        return redirect('home')
    return render(request,'sistema/verRespuesta.html',{'respuestas':respuestas})

def reasignar(request,dni):
    miembro=Miembro.objects.get(dni=dni)
    usr=CustomUser.objects.get(miembro__dni=dni)
    reuniones=Reunion.objects.filter(grupo__encargado=usr.id,borrado=False) 
    
    if request.method=='POST':
        print(request.POST)
        reuniones_encargado=request.POST.getlist('reunion-encargado')
        print('reuniones:',reuniones_encargado) #esto devuelve toda una lista que la voy a ir corando
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
                    msj=Mensaje.objects.get(id=5)
                    mensaje=msj.mensaje
                    miembros=[]
                    usr=CustomUser.objects.get(id=reunion.grupo.encargado)
                    mb_new=Miembros.objects.get(dni=usr.miembro_id)
                    miembros.append(mb_new)
                    asunto = msj.tipo
                    enviarWhatsapp(mensaje,miembros)
                    mensaje += 'El miembro ' + miembro.nombre + 'fue añadido a tu reunion ' + reunion.nombre 
                    enviarMail(miembros,asunto,mensaje)
                    #hasta aca avisamos al lider, ahora vamos al mb
                    miembros.clear()
                    miembros.append(mb)
                    mensaje=msj.mensaje + 'Fuiste añadido a la reunion ' + reunion.nombre 
                    enviarWhatsapp(miembros,mensaje) #le mandamos whatsapp
                    mensaje = msj.mensaje + 'Fuiste añadido a la reunion ' + reunion.nombre + ' habla con ' + mb_new.nombre+' para mas informacion'
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
                
    
    return render(request,'sistema/reasignar.html',{'miembro':miembro,'reuniones':reuniones})

def crearRol(request):
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

def verRol(request):
    roles=Rol.objects.all()
    return render(request,'sistema/verRol.html',{'roles':roles})

def editarRol(request,id_rol):
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

def eliminarRol(request,id_rol):
    rol=Rol.objects.get(id_rol=id_rol)
    if CustomUser.objects.filter(rol = rol).exists():
        messages.error(request, 'NO SE PUEDE ELIMINAR EL ROL: existen usuarios con dicho rol') 
        return redirect('/sistema/verRol')
    else:
        rol.borrado=True
        rol.save()
        return redirect('/sistema/verRol/')

def validarRol(request):
    nombre = request.GET.get('nombre')
    data = {
        'is_taken': Rol.objects.filter(nombre=nombre).exists()
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
        #bueno la idea ahora es ver en que horario se da esta reunion y ver que usuario tiene libre ese horario
        #si ninguno tiene, entonces vemos el domicilio, a ver a quien le queda mas cerca
        #y ver a que grupo de personas atiende esa persona tmb, por ejemplo si el grupo es femenino vemos una chica
        hs_rn=reunion.horario
        if Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta).exists():
            horarios=Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta)
            for horario in horarios:
                if Miembro.objects.filter(horario_disponible=horario).exclude(dni=mb_encargado.dni).exists():
                    miembros=Miembro_Horario_Disponible.objects.filter(horario=horario).exclude(dni=mb_encargado.dni)
                    #bien aca traje todos los miembros que tienen ese hs disponible a continuacion veo si hay un usr
                    for miembro in miembros:
                        if Usuario.objects.filter(miembro=miembro.dni).exists():
                            usrs=Usuario.objects.filter(miembro=miembro.dni)
                            for usr in usrs: #por cada usuario que tenga asosiado un miembro con horario disponible
                                # si concide el sexo del mb con el del grupo o si grupo admite ambos,funciona para femenino o masculino
                                if usr.miembro.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos": #si los sexos coinciden entonces recomiendo
                                    if usr.miembro.domicilio.barrio == reunion.domicilio.barrio:
                                        if not(mb in best_usr_recomendados):
                                            best_usr_recomendados.append(miembro) #el mejor
                                    else:
                                        if not(miembro in usr_recomendados):
                                            usr_recomendados.append(miembro) #no es tan weno
                        else: #aca no hay ningun user, entonces... vamos por miembros del mismo genero
                                if mb.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos":
                                    if not(miembro in usr_recomendados):
                                        miembro_recomendados.append(miembro)
                
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
                                        mb = usr.miembro
                                        # si concide el sexo del mb con el del grupo o si grupo admite ambos,funciona para femenino o masculino
                                        if mb.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos": #si los sexos coinciden entonces recomiendo
                                            if not(mb in usr_recomendados):
                                                usr_recomendados.append(mb)
                                            #aca no pregunto por el domicilio porque ya tamos en el domicilio XD osea no es best porque no tiene hs disponible
                                else: #aca hay cura, no tienen hs disponible, no hay usr, pero hay miembros en ese barrio
                                    if miembro.sexo == reunion.grupo.sexo or reunion.grupo.sexo=="Ambos":
                                        if not(miembro in mb_recomendados):
                                            mb_recomendados.append(miembro) #esto ya es para la ultima opcion
                                        
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
                        en=Custom.objects.get(id=grupito.encargado) #en=encargado
                        mb=en.miembro
                        if not(mb in usr_recomendados):
                            usr_recomendados.append(mb)
                if not(usr_recomendados) and not(mb_recomendados): #aca si que no hay nada de nada, entonces vamos a darle usr del mismo genero
                    if CustomUser.objects.filter(miembro__sexo=reunion.grupo.sexo).exclude(id=request.user.id).exists():
                        usrs=CustomUser.objects.filter(miembro__sexo=reunion.grupo.sexo).exclude(id=request.user.id)
                        for usr in usrs:
                            mb=usr.miembro
                            if not(mb in usr_recomendados):
                                usr_recomendados.append(mb)
                    else:
                        print('weno esto si que ya es imposible china xd')   
        if best_usr_recomendados:
            serializer=MiembroSerializer(best_usr_recomendados,many=True)
        elif usr_recomendados:
            serializer=MiembroSerializer(usr_recomendados,many=True)
        elif mb_recomendados:
            serializer=MiembroSerializer(mb_recomendados,many=True)
        result=dict()
        result = serializer.data
        return JSONResponse(result)

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
def reunionList(request):
    rn=request.GET.get('rn')
    if request.method =='GET':
        rn_base=Reunion.objects.get(nombre=rn) #no se si me va a dejar
        #vemos si hay una reunion posible para recomendar, osea aca ya entran las del mismo tipo
        encargado=rn_base.grupo.encargado
        rn_recomendada=[]
        dic=[]
        i=0
        if Reunion.objects.filter(tipo_reunion=rn_base.tipo_reunion).exclude(grupo__encargado=encargado).exists():
            reuniones=Reunion.objects.filter(tipo_reunion=rn_base.tipo_reunion).exclude(grupo__encargado=encargado)
            miembros=rn_base.grupo.miembro.all()
            for miembro in miembros:
                best_rn=[]
                rn=[]
                for reunion in reuniones:
                    if reunion.grupo.sexo=="Ambos" or reunion.grupo.sexo==rn_base.grupo.sexo:
                        hs_rn=reunion.horario
                        if Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta).exists():
                            horarios=Horario_Disponible.objects.filter(dia=hs_rn.dia,desde__gte=hs_rn.desde,hasta__lte=hs_rn.hasta)
                            for horario in horarios:
                                if Miembro.objects.filter(dni=miembro.dni,horario_disponible=horario).exists():
                                    barrio=miembro.domicilio.barrio
                                    if barrio == reunion.domicilio.barrio:
                                        best_rn.append(reunion) #ESTA es la mejor reunion para recomendar
                                    else:
                                        rn.append(reunion) #Esta voy a ocupar si no es la mejor reunion
                                        #esta reunion coincide con los horarios libres de las personas
                                elif miembro.domicilio.barrio == reunion.domicilio.barrio:
                                        rn.append(reunion) #No coincide con los horarios libres pero si con la ubicacion
                                else: #bueno aca no hay en el mismo barrio ni en el mismo horario
                                    #tonces le pongo la reunion del mismo tipo al menos y genero
                                    rn.append(reunion)
                        else: #aca no tienen el mismo hs disponible las reuniones pero pueden tener una ubicacion cerca
                            if miembro.domicilio.barrio == reunion.domicilio.barrio:
                                rn.append(reunion) #no es la mejor para ese miembro pero bueno
                    else:
                        print('ayayayay puede existir otras reuniones todavia tranqui')
                
                if best_rn:
                    rn_recomendada.append(best_rn[0])#solo una xD
                elif rn:
                    rn_recomendada.append(rn[0])

                print('------------------------------------///------------------------------')

                dic.append({'reunion': rn_recomendada[i].nombre, 'nombre':miembro.apellido + ', ' + miembro.nombre , 'id_reunion':str(rn_recomendada[i].id_reunion),'id_miembro':str(miembro.dni)}) 
                #aca confio con todo mi coracioncito que encontro una rn recomendada
                i += 1

            #aca estoy adentro del for de mb

        #weno no tiene chiste que vuelva a recorrer todo de nuevo pero bueno no me manejo bien con arrays
        #dic = {'reunion': change.field, 'nombre':change.old, 'id_reunion':change.new}

        if not(rn_recomendada):   
            data = {
                'is_taken': True
            }
            if data['is_taken']:
                data['error_message']  = 'No hay Reunion Recomendada'
            print(data)
            return JsonResponse(data)
        else:
            serializer=ReunionSerializer(rn_recomendada,many=True)
            result=dict()
            result = serializer.data
            return JSONResponse(dic)

def filtros_estado_miembro(request):
    desde = request.GET['desde']
    hasta = request.GET['hasta']
    print(desde)
    print(hasta)
    cant_mb=0 #cantidad de estados muy buenos
    cant_b=0  #cantidad de estados buenos
    cant_m=0  #cantidad de estados medios
    cant_c=0  #cantidad de estados criticos

    #Me aseguro de tener los datos que eligió y aplico los filtros
    if request.GET['desde'] == '' and request.GET['hasta'] =='': #si no eligio nada weno le muestro todos los actuales
        usuarios= CustomUser.objects.filter(is_active=True)
        cant_total=len(list(usuarios))
        for usuario in usuarios:
            estado = Estado.objects.filter(usuario_id=usuario.id).first()
            print('estado: ',estado)
            if estado != None:
                if estado.estado == 'Muy Bueno':
                    cant_mb += 1
                if estado.estado == 'Bueno':
                    cant_b += 1
                if estado.estado == 'Medio':
                    cant_m += 1
                if estado.estado == 'Pendiente' or estado.estado == 'Critico' : #critico que falta confirmar
                    cant_c += 1
            else: #si nunca registro un estado es porque esta mb, nunca falto consecutivamente ni nada
                cant_mb += 1 
        #bien ahora porcentajes
        if cant_total != 0:
            cant_mb = (cant_mb * 100) / cant_total
            cant_b = (cant_b * 100) / cant_total
            cant_m = (cant_m * 100) / cant_total
            cant_c = (cant_c * 100) / cant_total
    else: #es porque hay un desde y/o un hasta
        if request.GET['desde'] != '' and request.GET['hasta'] !='':
            #castear hasta pa que sea un timedate
            new_h = datetime.datetime.strptime(hasta, '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M:%S.%f')
            print('new_h: ', new_h)
            usuarios= CustomUser.objects.filter(date_joined__lte=new_h) #traigo todos los usr que estaban creados antes de la fecha max (hasta)
            cant_total=len(list(usuarios))
            for usuario in usuarios:
                estado= Estado.objects.filter(usuario_id=usuario.id,fecha__range=(desde,hasta)).first()
                print('estado: ',estado)
                if estado != None:
                    if estado.estado == 'Muy Bueno':
                        cant_mb += 1
                    if estado.estado == 'Bueno':
                        cant_b += 1
                    if estado.estado == 'Medio':
                        cant_m += 1
                    if estado.estado == 'Pendiente' or estado.estado == 'Critico' : #critico que falta confirmar
                        cant_c += 1
                else: #si no registro un estado en ese rango voy a ver el ultimo estado que tenia
                    estado = Estado.objects.filter(usuario_id=usuario.id,fecha__lte=desde).last()
                    if estado != None:
                        if estado.estado == 'Pendiente' or estado.estado == 'Critico' : #critico que falta confirmar
                            cant_c += 1
                        else:
                            cant_mb+=1 #osea si no esta suspendido ni nada entonces ta mb
                    else:
                        cant_mb+=1 #osea si no esta suspendido ni nada entonces ta mb
            if cant_total != 0:
                cant_mb = (cant_mb * 100) / cant_total
                cant_b = (cant_b * 100) / cant_total
                cant_m = (cant_m * 100) / cant_total
                cant_c = (cant_c * 100) / cant_total
        
    data = [cant_mb,cant_b,cant_m,cant_c]
    print("-----------------------------//-----------------------")
    print('data: ',data)
    return JSONResponse(data)

def filtros_estado_reunion(request):
    desde = request.GET['desde']
    hasta = request.GET['hasta']
    rn = request.GET['rn']

    print(desde)
    print(hasta)
    cant_mb=0 #cantidad de estados muy buenos
    cant_b=0  #cantidad de estados buenos
    cant_m=0  #cantidad de estados medios
    cant_c=0  #cantidad de estados criticos
    cant_s=0  #cantidad de miembros que no respondieron
    #lo primero y mas importante tiene que seleccionar una reunion
    if rn != '':
        if request.GET['desde'] == '' and request.GET['hasta'] =='': #si ambos son vacios muestro los actuales
            #bueno primero tengo que ver cual fue la ultima encuesta que le mande a esa reunion
            enc = Encuesta.objects.filter(reunion_id = rn, tipo = 2).order_by('-fecha_envio').first()
            #en teoria eso es orden descendente por eso obtengo el primero
            if enc != None:
                fecha=enc.fecha_envio
                encuestas = Encuesta.objects.filter(reunion_id=rn,tipo=2,fecha_envio=fecha).exclude(fecha_respuesta=None)#ahora obtengo todas las enviadas en esa fecha
                cant_total=len(list(encuestas)) #cantidad de encuestas enviadas a esa rn en esa fecha
                cant_s = Encuesta.objects.filter(reunion=rn, tipo=2,fecha_respuesta=None)
                cant_s = len(list(cant_s))
                cant_total += cant_s
                print('------------------')
                print('cantidad sin responder ', cant_s)
                print('cantidad total ', cant_total)
                print('------------------')
                for encuesta in encuestas:
                    estado= Estado_Reunion.objects.get(encuesta_id=encuesta.id_encuesta,reunion_id=rn,fecha=encuesta.fecha_respuesta)
                    print('estado: ',estado)
                    if estado.estado == 'Muy Bueno':
                        cant_mb += 1
                    if estado.estado == 'Bueno':
                        cant_b += 1
                    if estado.estado == 'Medio':
                        cant_m += 1
                    if estado.estado == 'Critico' :
                        cant_c += 1
                #bien ahora porcentajes
                if cant_total != 0:
                    cant_mb = (cant_mb * 100) / cant_total
                    cant_b = (cant_b * 100) / cant_total
                    cant_m = (cant_m * 100) / cant_total
                    cant_c = (cant_c * 100) / cant_total
                    cant_s = (cant_s * 100) / cant_total
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
                    estado= Estado_Reunion.objects.get(encuesta_id=encuesta.id_encuesta,reunion_id=rn,fecha=encuesta.fecha_respuesta)
                    print('estado: ',estado)
                    if estado.estado == 'Muy Bueno':
                        cant_mb += 1
                    if estado.estado == 'Bueno':
                        cant_b += 1
                    if estado.estado == 'Medio':
                        cant_m += 1
                    if estado.estado == 'Critico' :
                        cant_c += 1
                #bien ahora porcentajes
                if cant_total != 0:
                    cant_mb = (cant_mb * 100) / cant_total
                    cant_b = (cant_b * 100) / cant_total
                    cant_m = (cant_m * 100) / cant_total
                    cant_c = (cant_c * 100) / cant_total
                    cant_s = (cant_s * 100) / cant_total
            
        
        data = [cant_mb,cant_b,cant_m,cant_c,cant_s]
        if cant_mb ==0 and cant_b==0 and cant_m == 0 and cant_s==0 :
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
        reunion= Reunion.objects.filter(nombre=rn).last()
        rn = reunion.id_reunion
    else:
        rn=''
    print('REUNION ', rn)
    print('MIEMBRO ',mb)
    print('ROL: ',rol)
    cant_ast=0 #cantidad de estados muy buenos
    cant_fal=0   #cantidad de miembros que no respondieron
    #lo primero y mas importante tiene que seleccionar una reunion
    if request.GET['desde'] == '' and request.GET['hasta'] =='': #si ambos son vacios muestro los actuales
        if rn != '': #weno si no hay limite de fecha y rn esta seleccionado
            #bueno voy a traer todos los registros de asistencias de esa rn
            cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True)
            cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False)
            cant_ast= len(list(cant_ast))
            cant_fal= len(list(cant_fal))
            cant_total = cant_ast + cant_fal
        elif mb != 'null':
            cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True)
            cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False)
            cant_ast= len(list(cant_ast))
            cant_fal= len(list(cant_fal))
            cant_total = cant_ast + cant_fal
        elif rol != '': 
            usuarios = CustomUser.objects.filter(rol_id=rol)
            for usuario in usuarios:
                miembro = usuario.miembro
                cant_ast = Asistencia.objects.filter(miembro_id=miembro.dni,presente=True)
                cant_fal= Asistencia.objects.filter(miembro_id=miembro.dni,presente=False)
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal
    else: #weno si puso horarios tengo que ver cual
        if request.GET['desde'] != '' and request.GET['hasta'] !='':
            if rn != '': #Bueno si quiere filtar las asitencias de la reunion rn entre esas fechas entonces
                #bueno voy a traer todos los registros de asistencias de esa rn
                cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True,fecha__range=(desde,hasta))
                cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False,fecha__range=(desde,hasta))
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal

            elif mb != 'null':
                cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True,fecha__range=(desde,hasta))
                cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False,fecha__range=(desde,hasta))
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal
            elif rol != '': 
                usuarios = CustomUser.objects.filter(rol_id=rol)
                for usuario in usuarios:
                    miembro = usuario.miembro
                    cant_ast = Asistencia.objects.filter(miembro_id=miembro.dni,presente=True,fecha__range=(desde,hasta))
                    cant_fal= Asistencia.objects.filter(miembro_id=miembro.dni,presente=False,fecha__range=(desde,hasta))
                    cant_ast= len(list(cant_ast))
                    cant_fal= len(list(cant_fal))
                    cant_total = cant_ast + cant_fal
        elif request.GET['desde'] != '': #si entra aca es porque uno de los dos esta vacio, hay que ver cual
            #en este caso cargo solo el desde
            if rn != '': #Bueno si quiere filtar las asitencias de la reunion rn desde esa fecha en adelante
                #bueno voy a traer todos los registros de asistencias de esa rn
                cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True,fecha__gte=desde)
                cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False,fecha__gte=desde)
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal

            elif mb != 'null':
                cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True,fecha__gte=desde)
                cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False,fecha__gte=desde)
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal
            elif rol != '': 
                usuarios = CustomUser.objects.filter(rol_id=rol)
                for usuario in usuarios:
                    miembro = usuario.miembro
                    cant_ast = Asistencia.objects.filter(miembro_id=miembro.dni,presente=True,fecha__gte=desde)
                    cant_fal= Asistencia.objects.filter(miembro_id=miembro.dni,presente=False,fecha__gte=desde)
                    cant_ast= len(list(cant_ast))
                    cant_fal= len(list(cant_fal))
                    cant_total = cant_ast + cant_fal
        elif  request.GET['hasta'] != '': #en realidad con un else ya anda pero por la dudas
            if rn != '': #Bueno si quiere filtar las asitencias de la reunion rn desde esa fecha limita hacia atras
                #bueno voy a traer todos los registros de asistencias de esa rn
                cant_ast = Asistencia.objects.filter(reunion_id=rn,presente=True,fecha__lte=hasta)
                cant_fal = Asistencia.objects.filter(reunion_id=rn,presente=False,fecha__lte=hasta)
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal

            elif mb != 'null':
                cant_ast = Asistencia.objects.filter(miembro_id=mb,presente=True,fecha__lte=hasta)
                cant_fal= Asistencia.objects.filter(miembro_id=mb,presente=False,fecha__lte=hasta)
                cant_ast= len(list(cant_ast))
                cant_fal= len(list(cant_fal))
                cant_total = cant_ast + cant_fal
            elif rol != '': 
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
        data = [cant_ast,cant_fal]
        
            
            #ver de poner un mensajito
    print("-----------------------------//-----------------------")
    print('data: ',data)
    return JSONResponse(data)