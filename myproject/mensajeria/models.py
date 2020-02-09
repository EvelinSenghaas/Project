from django.db import models
from datetime import date
from simple_history.models import HistoricalRecords

class Tipo_Mensaje(models.Model):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=200)
    def __str__(self):
        return self.tipo
    
class Mensaje(models.Model):
    id = models.AutoField(primary_key=True)
    mensaje = models.CharField(max_length=200)
    tipo = models.ForeignKey(Tipo_Mensaje, on_delete=models.PROTECT)
    history = HistoricalRecords()

    def __str__(self):
        return self.mensaje
    