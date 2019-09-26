from django.urls import path
from .views import Asistencia,agregarAsistencia
from .views import crearTipo_Reunion,editarTipo_Reunion,listarTipo_Reunion
from .views import crearReunion,editarReunion,listarReunion
from .views import agregarEncuesta,agregarPregunta,agregarRespuesta,agregarHorario_Disponible
from .views import listarMiembro,crearMiembro,editarMiembro,eliminarMiembro
from .views import crearGrupo,listarGrupo,editarGrupo

urlpatterns = [
    path('crearTipo_Reunion/',crearTipo_Reunion,name='crearTipo_Reunion'),
    path('editarTipo_Reunion/<int:id_tipo_reunion>',editarTipo_Reunion,name='editarTipo_Reunion'),
    path('listarTipo_Reunion/',listarTipo_Reunion, name='listarTipo_Reunion'),
    path('crearReunion/',crearReunion,name='crearReunion'),
    path("listarReunion/", listarReunion, name='listarReunion'),
    path('editarReunion/<int:id_reunion>',editarReunion,name='editarReunion'),
    path('agregarAsistencia/',agregarAsistencia,name='agregarAsistencia'),
    path('agregarHorario_Disponible/',agregarHorario_Disponible,name='agregarHorario_Disponible'),
    path('agregarEncuesta/',agregarEncuesta,name ='agregarEncuesta'),
    path('agregarPregunta/',agregarPregunta,name='agregarPregunta'),
    path('agregarRespuesta/',agregarRespuesta,name='agregarRespuesta'),
    path('crearGrupo/',crearGrupo, name='crearGrupo'),
    path('listarGrupo/',listarGrupo,name='listarGrupo'),
    path('editarGrupo/<int:id_grupo>',editarGrupo,name='editarGrupo'),
    path('Asistencia/',Asistencia,name = 'Asistencia'),
    path('crearMiembro/',crearMiembro,name='crearMiembro'),
    path('listarMiembro/',listarMiembro,name='listarMiembro'),
    path('editarMiembro/<int:dni>',editarMiembro,name='editarMiembro'),
    path('eliminarMiembro/<int:dni>',eliminarMiembro, name='eliminarMiembro')
]
