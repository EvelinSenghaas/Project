import os
from twilio.rest import Client
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from .forms import *
from .models import *
from sistema.models import *

def configurarMensajes(request):
    mensajes=[]
    #el tipo 1 y 7 seran dinamicos
    tipo=Tipo_Mensaje.objects.all().exclude(id=1)
    for tp in tipo:
        if not(tp.id == 7):
            msj= Mensaje.objects.filter(tipo=tp)[:1]
            mensajes.append(msj[0])
    if request.method == 'POST':
        for tp in tipo:
            print(tp)
            msj = request.POST.get(str(tp))
            if not(Mensaje.objects.filter(tipo=tp,mensaje=msj).exists()):
                mensaje=Mensaje(mensaje=msj,tipo=tp)
                mensaje.changeReason= "Modificacion"
                mensaje.save()
        return redirect('home')
    
    return render(request,'mensajeria/configurarMensajes.html',{'mensajes':mensajes})

def enviarMail(miembros, asunto, mensaje):
    # subject = 'Thank you for registering to our site'
    # message = ' it  means a world to us '

    email_from = settings.EMAIL_HOST_USER    
    
    #Arma lista con todos los mail a avisar.
    para = []
    for miembro in miembros:
        contacto_usuario = miembro 
        para.append(contacto_usuario.correo)
    print('enviando mail')
    send_mail(asunto, mensaje, email_from, para) 
    print('ya ta?')

def enviarWhatsapp(mensaje,miembros):
    account_sid = 'AC26e164ae31f6ebd42ef0c40c567c469b' 
    auth_token = 'acae54e2314b668844bfebc74fb9a83a' 
    client = Client(account_sid, auth_token) 
    from_whatsapp_number='whatsapp:+14155238886'
    to_whatsapp_number='whatsapp:+5493764816893'
    #5493764675702 hernan
    print('mensaje: ', mensaje)
    mensaje=mensaje + ' revisa tu correo para mas informacion'
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
    
