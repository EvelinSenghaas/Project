from django.db import models
from django.contrib.auth.models import AbstractUser
from sistema.models import Miembro

class CustomUser(AbstractUser):
    miembro= models.ForeignKey(Miembro, on_delete=models.PROTECT)