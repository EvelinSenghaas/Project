from django.contrib import admin
from django.urls import path,include
from sistema.views import Home
from django.conf.urls.static import static
from django.conf import settings    
from django.views.generic.base import TemplateView 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sistema/',include(('sistema.urls','sistema'))),
    path('Home/',Home,name = 'home'),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('accounts/', include('accounts.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  
]
