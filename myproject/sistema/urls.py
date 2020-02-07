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
    path('agregarRespuestaReunion/<int:id_encuesta>',agregarRespuestaReunion,name='agregarRespuestaReunion'),
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
    path("verRespuesta/<int:id_encuesta>", verRespuesta, name="verRespuesta"),
    path("respuestaList/", respuestaList, name="respuestaList"),
    path("reasignar/<int:dni>", reasignar, name="reasignar"),
    path("recomendacionTable/", recomendacionTable, name="recomendacionTable"),
    path("miembrosList/", miembrosList, name="miembrosList"),
    path("reunionList/", reunionList, name="reunionList"),
    path("auditoria_detalles_miembro/<int:dni>/<int:id_auditoria>", auditoria_detalles_miembro, name="auditoria_detalles_miembro"),
    path("auditoria_detalles_reunion/<int:id>/<int:id_auditoria>", auditoria_detalles_reunion, name="auditoria_detalles_reunion"),
    path("estadistica_miembro/",estadistica_miembro, name="estadistica_miembro"),
    path("estadistica_reunion/",estadistica_reunion, name="estadistica_reunion"),
    path("estadistica_asistencias/",estadistica_asistencias, name="estadistica_asistencias"),
    path("filtros_estado_miembro/", filtros_estado_miembro, name="filtros_estado_miembro"),
    path("filtros_estado_reunion/", filtros_estado_reunion, name="filtros_estado_reunion"),
    path("filtros_asistencias/", filtros_asistencias, name="filtros_asistencias"),
]
