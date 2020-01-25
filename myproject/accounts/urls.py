# accounts/urls.py
from django.urls import path

from . import views
from .views import *


urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path("validarNombre/", validarNombre, name="validarNombre")
]
