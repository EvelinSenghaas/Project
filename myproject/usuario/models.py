from django.db import models
from django.contrib.auth.models import AbstractUser
from sistema.models import Miembro,Rol,Estado
from simple_history.models import HistoricalRecords


class CustomUser(AbstractUser):
    miembro= models.ForeignKey(Miembro, on_delete=models.PROTECT)
    rol=models.ForeignKey(Rol, on_delete=models.PROTECT)
    faltas=models.IntegerField("Faltas",null=True,default='0')
    history = HistoricalRecords()

class Estado_Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    usuario=models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    estado=models.ForeignKey(Estado, on_delete=models.PROTECT)
    confirmado=models.BooleanField(null=True)
    fecha=models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
