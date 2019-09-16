from django.db import models


class Tipo_Reunion(models.Model):
    id_tipo_reunion =  models.AutoField(primary_key = True)
    nombre=models.CharField('Nombre',max_length=200,blank = False, null = False)
    descripcion = models.CharField('Descripcion',max_length=200,blank = False, null = True)

class Reunion(models.Model):
    id_reunion=models.AutoField(primary_key=True)
    fecha = models.DateField('Fecha', auto_now=False, auto_now_add=False)
    hora = models.TimeField('Horario', auto_now=False, auto_now_add=False)
    tipo_reunion=models.ForeignKey(Tipo_Reunion, on_delete=models.CASCADE)

class Domicilio(models.Model):
    id_domicilio = models.AutoField(primary_key=True)
    calle=models.CharField('Calle', max_length=100,blank=False,null=False)
    nro=models.CharField('Numero', max_length=50,blank=False,null=False)
    barrio = models.CharField('Barrio', max_length=100,blank=False,null=False)
    localidad=models.CharField('Localidad', max_length=50,blank=False,null=False)
    provincia=models.CharField('Provincia', max_length=50,blank=False,null=False)
    reunion=models.ForeignKey(Reunion, on_delete=models.CASCADE)    

class Miembro(models.Model):
    dni=models.BigIntegerField(primary_key=True)
    nombre=models.CharField('Nombre',max_length=200,blank = False, null = False)
    apellido = models.CharField('Apellido',max_length=200,blank = False, null = False)
    nacionalidad = models.CharField('Nacionalidad', max_length=100,blank=False, null = False)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', auto_now=False, auto_now_add=False)
    estado_civil = models.CharField('Estado Civil', max_length=100,blank=False,null=False)
    cant_hijo = models.IntegerField('Cantidad de Hijos',null=True)
    trabaja = models.BooleanField('Trabaja')
    domicilio=models.ForeignKey(Domicilio, on_delete=models.CASCADE)
    correo=models.EmailField('e-mail', max_length=100,null=True)

class Grupo(models.Model):
    id_grupo=models.AutoField(primary_key=True)
    nombre=models.CharField('Nombre', max_length=50,blank=False,null=False)
    miembro=models.ManyToManyField(Miembro)


class Asistencia(models.Model):
    id_asistencia=models.AutoField(primary_key=True)
    presente=models.BooleanField('Presente')
    justificacion=models.TextField('Justificacion',blank=False,null=True)
    miembro=models.ForeignKey(Miembro, on_delete=models.CASCADE)
    reunion=models.ForeignKey(Reunion, on_delete=models.CASCADE)

class Tipo_Telefono(models.Model):
    id_tipo_telefono=models.AutoField(primary_key=True)
    tipo=models.CharField('Tipo', max_length=50,blank=False,null=False)#puede ser celular,fijo
    empresa=models.CharField('Empresa', max_length=50,blank=False,null=False)#claro,personal,tuenti,movistar

class Telefono(models.Model):
    id_telefono=models.AutoField(primary_key=True)
    prefijo=models.IntegerField('Prefijo')
    numero=models.IntegerField('Numero')
    whatsapp=models.BooleanField('Whatsapp')
    miembro=models.ForeignKey(Miembro, on_delete=models.CASCADE)
    tipo_telefono=models.ForeignKey(Tipo_Telefono, on_delete=models.CASCADE)

class Horario_Disponible(models.Model):
    id_horario_disponible=models.AutoField(primary_key=True)
    dia=models.CharField('Tipo', max_length=50,blank=False,null=False)
    hora=models.TimeField('Hora', auto_now=False, auto_now_add=False)
    miembro=models.ForeignKey(Miembro, on_delete=models.CASCADE)

class Encuesta(models.Model):
    id_fecha_envio=models.AutoField(primary_key=True)
    fecha_envio=models.DateField('Fecha Envio',auto_now=False, auto_now_add=False)
    miembro=models.ForeignKey(Miembro, on_delete=models.CASCADE)    

class Pregunta(models.Model):
    id_pregunta=models.AutoField(primary_key=True)
    descripcion=models.CharField('Pregunta', max_length=50,blank=False,null=False)
    encuesta=models.ForeignKey(Encuesta, on_delete=models.CASCADE)

class Respuesta(models.Model):
    id_respuesta=models.AutoField(primary_key=True)
    descripcion=models.CharField('Respuesta', max_length=50,blank=False,null=False)
    puntaje=models.IntegerField('Puntaje')
    pregunta=models.OneToOneField(Pregunta, on_delete=models.CASCADE)



