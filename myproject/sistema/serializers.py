from rest_framework import serializers
from .models import Provincia,Localidad,Barrio,Asistencia

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

class AsistenciaSerializer(serializers.ModelSerializer):
    #localidad = LocalidadSerializer()
    class Meta:
        model = Asistencia
        fields=['miembro','reunion']
