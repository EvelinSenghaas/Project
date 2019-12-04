from django.contrib import admin
from django.urls import path,include
from sistema.views import Home
from django.conf.urls.static import static
from django.conf import settings    
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from usuario.views import Login, logoutUsuario

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sistema/',include(('sistema.urls','sistema'))),
    path('Home/',Home,name = 'home'),
    path('accounts/login/', Login.as_view(), name='login'),
    path('accounts/logout/', login_required(logoutUsuario), name='logout')
]

