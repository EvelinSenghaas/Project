from django.shortcuts import render,redirect
from .forms import MiembroForm,Tipo_ReunionForm,ReunionForm,AsistenciaForm,Horario_DisponibleForm,Tipo_TelefonoForm
from .forms import TelefonoForm,EncuestaForm,PreguntaForm,RespuestaForm,GrupoForm,DomicilioForm
from .models import Miembro,Grupo,Tipo_Reunion,Reunion,Tipo_Telefono,Telefono,Domicilio,Horario_Disponible

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
    grupos = Grupo.objects.all()
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

def listarMiembro(request):
    if request.method == 'POST':
        return redirect('home')
    else:
        miembros = Miembro.objects.all()
    return render(request,'sistema/listarMiembro.html',{'miembros':miembros})

def crearMiembro(request):
    if request.method == 'POST':    
        nombre=request.POST.get('nombre')
        apellido=request.POST.get('apellido')
        nacionalidad=request.POST.get('nacionalidad')
        dni=request.POST.get('dni')
        tipo_dni=request.POST.get('tipo_dni')
        fecha_nacimiento=request.POST.get('fecha_nacimiento')
        estado_civil=request.POST.get('estado_civil')
        cant_hijo=request.POST.get('cant_hijo')
        trabaja=request.POST.get('trabaja')
        correo =request.POST.get('correo')
        sexo =request.POST.get('sexo')

        tipo=request.POST.get('tipo')
        empresa=request.POST.get('empresa')

        prefijo=request.POST.get('prefijo')
        numero=request.POST.get('numero')
        whatsapp=request.POST.get('whatsapp')

        calle=request.POST.get('calle')
        nro=request.POST.get('nro')
        mz=request.POST.get('mz')
        provincia=request.POST.get('provincia')
        localidad=request.POST.get('localidad')
        barrio=request.POST.get('barrio')
        departamento=request.POST.get('departamento')
        piso=request.POST.get('piso')

        dia=request.POST.get('dia')
        desde=request.POST.get('desde')
        hasta=request.POST.get('hasta')
        horario_form=Horario_Disponible(dia=dia,desde=desde,hasta=hasta)
        domicilio_form=Domicilio(calle=calle,nro=nro,mz=mz,provincia=provincia,localidad=localidad,barrio=barrio,departamento=departamento,piso=piso)
        domicilio_form.save()
        tipo_telefono_form=Tipo_Telefono(tipo=tipo,empresa=empresa)
        tipo_telefono_form.save()
        telefono_form=Telefono(prefijo=prefijo,numero=numero,whatsapp=whatsapp,tipo_telefono=tipo_telefono_form)
        telefono_form.save()
        horario_form.save()
        miembro_form=Miembro(nombre=nombre,apellido=apellido,nacionalidad=nacionalidad,dni=dni,tipo_dni=tipo_dni,fecha_nacimiento=fecha_nacimiento,estado_civil=estado_civil,cant_hijo=cant_hijo,trabaja=trabaja,correo=correo,sexo=sexo,domicilio=domicilio_form,telefono=telefono_form,horario_disponible=horario_form)
        #if miembro_form.is_valid() and domicilio_form.is_valid() and tipo_telefono_form.is_valid() and telefono_form.is_valid():
        miembro_form.save()

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
    id_telefono=miembro.telefono.id_telefono
    telefono=Telefono.objects.get(id_telefono=id_telefono)
    id_tipo_telefono=telefono.tipo_telefono.id_tipo_telefono
    tipo_telefono=Tipo_Telefono.objects.get(id_tipo_telefono=id_tipo_telefono)
    id_horario=miembro.horario_disponible.id_horario_disponible
    horario_disponible = Horario_Disponible.objects.get(id_horario_disponible=id_horario)

    if request.method == 'GET':
        miembro_form=MiembroForm(instance = miembro)
        domicilio_form=DomicilioForm(instance=domicilio)
        tipo_telefono_form=Tipo_TelefonoForm(instance=tipo_telefono)
        telefono_form=TelefonoForm(instance=telefono)
        horario_form=Horario_DisponibleForm(instance=horario_disponible)

    else:
        print('POSTea3')
        miembro_form=MiembroForm(request.POST,instance=miembro)
        domicilio_form=DomicilioForm(request.POST,instance=domicilio)
        tipo_telefono_form=Tipo_TelefonoForm(request.POST,instance=tipo_telefono)
        telefono_form=TelefonoForm(request.POST,instance=telefono)
        horario_form=Horario_DisponibleForm(request.POST,instance=horario_disponible)
        
        '''miembro_form.nombre=request.POST.get('nombre')
        miembro_form.apellido=request.POST.get('apellido')
        miembro_form.nacionalidad=request.POST.get('nacionalidad')
        miembro_form.dni=request.POST.get('dni')
        miembro_form.tipo_dni=request.POST.get('tipo_dni')
        miembro_form.fecha_nacimiento=request.POST.get('fecha_nacimiento')
        miembro_form.estado_civil=request.POST.get('estado_civil')
        miembro_form.cant_hijo=request.POST.get('cant_hijo')
        miembro_form.trabaja=request.POST.get('trabaja')
        miembro_form.correo =request.POST.get('correo')
        miembro_form.sexo =request.POST.get('sexo')
        #miembro_form.barrio=request.POST.get('barrio')

        tipo_telefono_form.tipo=request.POST.get('tipo')
        tipo_telefono_form.empresa=request.POST.get('empresa')

        telefono_form.prefijo=request.POST.get('prefijo')
        telefono_form.numero=request.POST.get('numero')
        telefono_form.whatsapp=request.POST.get('whatsapp')

        domicilio_form.calle=request.POST.get('calle')
        domicilio_form.nro=request.POST.get('nro')
        domicilio_form.mz=request.POST.get('mz')
        domicilio_form.provincia=request.POST.get('provincia')
        domicilio_form.localidad=request.POST.get('localidad')
        domicilio_form.barrio=request.POST.get('barrio')'''
        domicilio_form.save()
        miembro_form.save()
        tipo_telefono_form.save()
        telefono_form.save()
        return redirect('/sistema/listarMiembro')

    return render(request,'sistema/editarMiembro.html',{'miembro_form':miembro_form,'domicilio_form':domicilio_form,'tipo_telefono_form':tipo_telefono_form,'telefono_form':telefono_form})

def eliminarMiembro(request,dni):
    miembro = Miembro.objects.get(dni=dni)
    id_domicilio=miembro.domicilio.id_domicilio
    domicilio=Domicilio.objects.get(id_domicilio=id_domicilio)
    id_telefono=miembro.telefono.id_telefono
    telefono=Telefono.objects.get(id_telefono=id_telefono)
    id_tipo_telefono=telefono.tipo_telefono.id_tipo_telefono
    tipo_telefono=Tipo_Telefono.objects.get(id_tipo_telefono=id_tipo_telefono)
    domicilio.delete()
    miembro.delete()
    telefono.delete()
    tipo_telefono.delete()
    return redirect('/sistema/listarMiembro')

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
    tipo_reuniones = Tipo_Reunion.objects.all()
    return render(request,'sistema/listarTipo_Reunion.html',{'tipo_reuniones':tipo_reuniones})

def crearReunion(request):
    if request.method == 'POST':
        reunion_form=ReunionForm(request.POST)
        if reunion_form.is_valid():
            reunion_form.save()
            return redirect('/sistema/listarReunion')
    else:
        reunion_form=ReunionForm()
    return render(request,'sistema/crearReunion.html',{'reunion_form':reunion_form})

def editarReunion(request,id_reunion):
    reunion = Reunion.objects.get(id_reunion=id_reunion)
    if request.method == 'GET':
        reunion_form=ReunionForm(instance = reunion)
    else:
        reunion_form=ReunionForm(request.POST,instance=reunion)
        if reunionf_form.is_valid():
            reunion_form.save()
        return redirect('/sistema/listarReunion')
    return render(request,'sistema/crearReunion.html',{'reunion_form':reunion_form})

def listarReunion(request):
    reuniones = Reunion.objects.all()
    return render(request,'sistema/listarReunion.html',{'reuniones':reuniones})      

def agregarAsistencia(request):
    if request.method == 'POST':
        asistencia_form=AsistenciaForm(request.POST)
        if asistencia_form.is_valid():
            asistencia_form.save()
            return redirect('home')
    else:
        asistencia_form=AsistenciaForm()
    return render(request,'sistema/agregarAsistencia.html',{'asistencia_form':asistencia_form})

    if request.method == 'POST':
        tipo_telefono_form = Tipo_TelefonoForm(request.POST)
        if tipo_telefono_form.is_valid():
            tipo_telefono_form.save()
            return redirect('home')
    else:
        tipo_telefono_form = Tipo_TelefonoForm()
    return render(request,'sistema/agregarTipo_Telefono.html',{'tipo_telefono_form':tipo_telefono_form})   

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