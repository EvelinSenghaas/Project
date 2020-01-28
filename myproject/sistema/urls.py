from django.urls import path
from .views import *

urlpatterns = [
    path('crearTipo_Reunion/',crearTipo_Reunion,name='crearTipo_Reunion'),
    path('editarTipo_Reunion/<int:id_tipo_reunion>',editarTipo_Reunion,name='editarTipo_Reunion'),
    path('listarTipo_Reunion/',listarTipo_Reunion, name='listarTipo_Reunion'),
    path('eliminarTipo_Reunion/<int:id_tipo_reunion>',eliminarTipo_Reunion,name='eliminarTipo_Reunion'),
    path('crearReunion/',crearReunion,name='crearReunion'),
    path("listarReunion/", listarReunion, name='listarReunion'),
    path('editarReunion/<int:id_reunion>',editarReunion,name='editarReunion'),
    path('eliminarReunion/<int:id_reunion>',eliminarReunion,name='eliminarReunion'),
    path('agregarAsistencia/',agregarAsistencia,name='agregarAsistencia'),
    path('agregarHorario_Disponible/',agregarHorario_Disponible,name='agregarHorario_Disponible'),
    path('agregarEncuesta/',agregarEncuesta,name ='agregarEncuesta'),
    path('agregarPregunta/',agregarPregunta,name='agregarPregunta'),
    path('agregarRespuesta/',agregarRespuesta,name='agregarRespuesta'),
    path('crearGrupo/',crearGrupo, name='crearGrupo'),
    path('listarGrupo/',listarGrupo,name='listarGrupo'),
    path('editarGrupo/<int:id_grupo>',editarGrupo,name='editarGrupo'),
    path('eliminarGrupo/<int:id_grupo>',eliminarGrupo,name='eliminarGrupo'),
    path('crearMiembro/',crearMiembro,name='crearMiembro'),
    path('listarMiembro/',listarMiembro,name='listarMiembro'),
    path('editarMiembro/<int:dni>',editarMiembro,name='editarMiembro'),
    path('eliminarMiembro/<int:dni>',eliminarMiembro, name='eliminarMiembro'),
    path("validarMiembro/", validarMiembro, name="validarMiembro"),
    path("validarGrupo/", validarGrupo, name="validarGrupo"),
    path("provinciasList/", provinciasList, name="provinciasList"),
    path("localidadesList/", localidadesList, name="localidadesList"),
    path("barriosList/", barriosList, name="barriosList"),
    path("AsistenciaTable/", AsistenciaTable, name="AsistenciaTable"),
    path("GrupoTable/", GrupoTable, name="GrupoTable"),
    path("MiembroTable/", MiembroTable, name="MiembroTable"),
    path("sexoList/", sexoList, name="sexoList"),
    path("configuracion/", configuracion, name="configuracion"),
    path("auditoriaMiembro/", auditoriaMiembro, name="auditoriaMiembro"),
    path("auditoriaReunion/", auditoriaReunion, name="auditoriaReunion"),
    path("verAsistencia/",verAsistencia,name="verAsistencia"),
    path("EncuestaTable/", EncuestaTable, name="EncuestaTable"),
    path("crearRol/", crearRol, name="crearRol"),
    path("verRol/", verRol, name="verRol"),
    path("editarRol/<int:id_rol>", editarRol, name="editarRol"),
    path("eliminarRol/<int:id_rol>", eliminarRol, name="eliminarRol"),
    path("validarRol/", validarRol, name="validarRol"),
    path("validarPregunta/", validarPregunta, name="validarPregunta"),
    path("eliminarPregunta/<int:id_pregunta>",eliminarPregunta, name="eliminarPregunta"),
    path("opcionesList/", opcionesList, name="opcionesList"),
]
