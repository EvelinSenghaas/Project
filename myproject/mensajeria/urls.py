from sistema.views import Home
from django.urls import path
from .views import *

urlpatterns = [
    path("configurarMensajes/", configurarMensajes, name="configurarMensajes"),
    #path("enviarWhatsapp/", enviarWhatsapp, name="enviarWhatsapp")
]



