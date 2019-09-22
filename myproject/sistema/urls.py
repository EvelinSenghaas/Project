from django.urls import path
from .views import Asistencia,agregarAsistencia
from .views import crearTipo_Reunion,crearReunion
from .views import agregarTipo_Telefono,agregarTelefono
from .views import agregarEncuesta,agregarPregunta,agregarRespuesta,crearGrupo,agregarHorario_Disponible
from .views import listarMiembro,crearMiembro,editarMiembro

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
    path('crearGrupo/',crearGrupo, name='crearGrupo'),
    path('Asistencia/',Asistencia,name = 'Asistencia'),
    path('listarMiembro/',listarMiembro,name='listarMiembro'),
    path('editarMiembro/<int:dni>',editarMiembro,name='editarMiembro')
]
