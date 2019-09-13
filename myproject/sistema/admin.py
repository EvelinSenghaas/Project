from django.contrib import admin
from .models import Miembro,Grupo,Tipo_Reunion,Reunion,Domicilio,Asistencia,Tipo_Telefono,Telefono,Horario_Disponible,Encuesta,Pregunta,Respuesta

admin.site.register(Miembro)
admin.site.register(Grupo)
admin.site.register(Tipo_Reunion)
admin.site.register(Reunion)
admin.site.register(Domicilio)
admin.site.register(Asistencia)
admin.site.register(Tipo_Telefono)
admin.site.register(Telefono)
admin.site.register(Horario_Disponible)
admin.site.register(Encuesta)
admin.site.register(Pregunta)
admin.site.register(Respuesta)
