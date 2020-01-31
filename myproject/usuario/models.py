from django.db import models
from django.contrib.auth.models import AbstractUser
from sistema.models import Miembro,Rol

class CustomUser(AbstractUser):
    miembro= models.ForeignKey(Miembro, on_delete=models.PROTECT)
    rol=models.ForeignKey(Rol, on_delete=models.PROTECT)
    faltas=models.IntegerField("Faltas",null=True,default='0')

class Estado(models.Model):
    id = models.AutoField(primary_key=True)
    usuario=models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    estado=models.CharField(max_length=50)
    confirmado=models.BooleanField(null=True)
    fecha=models.DateField( auto_now_add=True)