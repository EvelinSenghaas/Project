from rest_framework import serializers
from .models import Provincia,Localidad,Barrio,Asistencia, Miembro, Grupo

class ProvinciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provincia
        fields = ['id_provincia','provincia']

class LocalidadSerializer(serializers.ModelSerializer):
    provincia = ProvinciaSerializer()
    class Meta:
        model = Localidad
        fields = ['id_localidad','localidad','provincia']

class BarrioSerializer(serializers.ModelSerializer):
    localidad = LocalidadSerializer()
    class Meta:
        model = Barrio
        fields = ['id_barrio','barrio','localidad']

class MiembroSerializer(serializers.ModelSerializer):
    #grupo_set = GrupoSerializer(many=True)
    class Meta:
        model = Miembro
        fields=['dni','nombre','apellido']


class GrupoSerializer(serializers.ModelSerializer):
    miembro = MiembroSerializer(many=True)
    class Meta:
        model = Grupo
        fields=['miembro']


class AsistenciaSerializer(serializers.ModelSerializer):
    #localidad = LocalidadSerializer()
    class Meta:
        model = Asistencia
        fields=['miembro','reunion']
