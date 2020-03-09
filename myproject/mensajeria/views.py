import os
from twilio.rest import Client
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from .forms import *
from .models import *
from sistema.models import *

#implementar permisos y login aqui
def configurarMensajes(request):
    mensajes=[]
    #el tipo 1 y 7 seran dinamicos
    tipo=Tipo_Mensaje.objects.all().exclude(id=1)
    for tp in tipo:
        msj= Mensaje.objects.filter(tipo=tp).last()
        mensajes.append(msj)
    enc= Tipo_Encuesta.objects.get(id_tipo_encuesta=4)
    x= enc.cantidad
    if request.method == 'POST':
        x_new=request.POST.get('x')
        if x != x_new:
            print('nuevita la x')
            enc.cantidad=x_new
            enc.save()
        for tp in tipo:
            print(tp)
            msj = request.POST.get(str(tp))
            mensaje = Mensaje.objects.get(tipo=tp)
            if mensaje.mensaje != msj:
                mensaje.mensaje=msj
                mensaje.save()
                mensaje.changeReason= "Modificacion"
                mensaje.save()
        return redirect('home')
    
    return render(request,'mensajeria/configurarMensajes.html',{'mensajes':mensajes,'x':x})

def enviarMail(miembros, asunto, mensaje):
    # subject = 'Thank you for registering to our site'
    # message = ' it  means a world to us '

    email_from = settings.EMAIL_HOST_USER    
    
    #Arma lista con todos los mail a avisar.
    para = []
    mb=Miembro.objects.get(dni=41788492)
    para.append(mb.correo)
    '''for miembro in miembros:
        contacto_usuario = miembro 
        para.append(contacto_usuario.correo)'''
    print('enviando mail')
    send_mail(asunto, mensaje, email_from, para) 
    print('ya ta?')

def enviarWhatsapp(mensaje,miembros):
    account_sid = 'AC26e164ae31f6ebd42ef0c40c567c469b' 
    auth_token = 'ccff833d6786f4885efcbb20a9681022' 
    client = Client(account_sid, auth_token) 
    from_whatsapp_number='whatsapp:+14155238886'
    to_whatsapp_number='whatsapp:+5493764816893'
    #5493764675702 hernan
    print('mensaje: ', mensaje)
    mensaje = mensaje + ' revisa tu correo para mas informacion'
            #to_whatsapp_number = 'whatsapp:+549'+ str(miembro.telefono.prefijo)+str(miembro.telefono.numero)
    message = client.messages.create(body=mensaje,from_= from_whatsapp_number,to=to_whatsapp_number)
            
        # else:
        #     #deberia ver el tema de telefono de contactos, pero veo si tiene mail
        #     if miembro.correo != None:
        #         if not(Mensaje.objects.filter(mensaje=mensaje).exists()):
        #             tipo = Tipo_Mensaje.objects.get(id=1)
        #             mensaje = Mensaje(mensaje=mensaje,tipo=tipo)
        #         else:
        #             mensaje=Mensaje.objects.filter(mensaje=mensaje)[:1]
        #             mensaje=Mensaje.objects.get(id=mensaje[0].id)
        #         asunto=mensaje.tipo
        #         mensaje=mensaje.mensaje
        #         miembros=[]
        #         miembros.append(miembro)
        #         enviarMail(miembros,asunto,mensaje)
        #     print("mira tu correo capa")
    
