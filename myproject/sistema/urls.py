from django.urls import path
from .views import crearMiembro,crearTipo_Reunion,crearReunion,agregarAsistencia,agregarHorario_Disponible,agregarTipo_Telefono
from .views import agregarTelefono,agregarEncuesta,agregarPregunta,agregarRespuesta,crearGrupo

urlpatterns = [
    path('crearMiembro/',crearMiembro,name='crearMiembro'),
    path('crearTipo_Reunion/',crearTipo_Reunion,name='crearTipo_Reunion'),
    path('crearReunion/',crearReunion,name='crearReunion'),
    path('agregarAsistencia/',agregarAsistencia,name='agregarAsistencia'),
    path('agregarHorario_Disponible/',agregarHorario_Disponible,name='agregarHorario_Disponible'),
    path('agregarTipo_Telefono/',agregarTipo_Telefono,name='agregarTipo_Telefono'),
    path('agregarTelefono/',agregarTelefono,name='agregarTelefono'),
    path('agregarEncuesta/',agregarEncuesta,name ='agregarEncuesta'),
    path('agregarPregunta/',agregarPregunta,name='agregarPregunta'),
    path('agregarRespuesta/',agregarRespuesta,name='agregarRespuesta'),
    path("crearGrupo/",crearGrupo, name='crearGrupo')
]
