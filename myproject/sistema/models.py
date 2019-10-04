from django.db import models
from datetime import date

class Tipo_Reunion(models.Model):
    id_tipo_reunion =  models.AutoField(primary_key = True)
    nombre=models.CharField('Nombre',max_length=200,blank = False, null = False)
    descripcion = models.CharField('Descripcion',max_length=200,blank = False, null = True)
    borrado = models.BooleanField('borrado',default=False)
    
    def __str__(self):
        return self.nombre 
    
class Domicilio(models.Model):
    id_domicilio = models.AutoField(primary_key=True)
    calle=models.CharField('Calle', max_length=100,blank=False,null=False)
    nro=models.CharField('Numero', max_length=50,blank=False,null=False)
    mz = models.CharField('Manzana', max_length=50,null=True,blank=True)
    departamento=models.CharField('Departamento', max_length=50,null=True,blank=True)
    piso=models.CharField('Piso', max_length=50,null=True,blank=True)
    barrio = models.CharField('Barrio', max_length=100,blank=False,null=False)
    localidad=models.CharField('Localidad', max_length=50,blank=False,null=False)
    provincia=models.CharField('Provincia', max_length=50,blank=False,null=False)
    borrado = models.BooleanField('borrado',default=False)

    
    def __str__(self):
        return self.barrio
    
class Horario_Disponible(models.Model):
    DIA=[
        ('Lunes','Lunes'),
        ('Martes','Martes'),
        ('Miercoles','Miercoles'),
        ('Jueves','Jueves'),
        ('Viernes','Viernes'),
        ('Sabado','Sabado'),
        ('Domingo','Domingo')
    ]
    id_horario_disponible=models.AutoField(primary_key=True)
    dia=models.CharField('dia',max_length=50,blank=False,null=False,choices=DIA)
    desde=models.TimeField('Desde', auto_now=False, auto_now_add=False,null=True)
    hasta=models.TimeField('Hasta', auto_now=False, auto_now_add=False,null=True)
    borrado = models.BooleanField('borrado',default=False)

class Tipo_Telefono(models.Model):
    TIPO={
        ('Movil','Movil'),
        ('Fijo','Fijo')
    }
    EMPRESA={
        ('Personal','Personal'),
        ('Claro','Claro'),
        ('Movistar','Movistar'),
        ('Tuenti','Tuenti'),
        ('Otro','Otro')
    }
    id_tipo_telefono=models.AutoField(primary_key=True)
    tipo=models.CharField('Tipo', max_length=50,blank=False,null=False,choices=TIPO)
    empresa=models.CharField('Empresa', max_length=50,blank=False,null=False,choices=EMPRESA)
    borrado = models.BooleanField('borrado',default=False)

    
    def __str__(self):
        return self.tipo
    
class Telefono(models.Model):
    id_telefono=models.AutoField(primary_key=True)
    prefijo=models.IntegerField('Prefijo',blank=True,null=True)
    numero=models.IntegerField('Numero')
    whatsapp=models.BooleanField('Whatsapp',default=True)
    tipo_telefono=models.ForeignKey(Tipo_Telefono, on_delete=models.PROTECT,null=True)
    borrado = models.BooleanField('borrado',default=False)    

    def __str__(self):
        return self.prefijo + self.numero
    
class Miembro(models.Model):
    TIPO=[
        ('DNI','DNI'),
        ('CUIL','CUIL'),
        ('CUIT','CUIT'),
        ('PASAPORTE','PASAPORTE')
    ]
    ESTADO_CIVIL=[
        ('Soltero/a','Soltero/a'),
        ('Casado/a','Casado/a'),
        ('Divorciado/a','Divorciado/a'),
        ('Viudo/a','Viudo/a')
    ]
    SEXO=[
        ('Masculino','Masculino'),
        ('Femenino','Femenino')
    ]
    tipo_dni = models.CharField('Tipo de DNI', max_length=20,choices=TIPO)
    dni=models.BigIntegerField('Documento',primary_key=True)
    nombre=models.CharField('Nombre',max_length=200,blank = False, null = False)
    apellido = models.CharField('Apellido',max_length=200,blank = False, null = False)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', auto_now=False, auto_now_add=False)
    estado_civil = models.CharField('Estado Civil',max_length=20,choices=ESTADO_CIVIL,blank=False,null=False)
    cant_hijo = models.IntegerField('Cantidad de Hijos',null=True)
    trabaja = models.BooleanField('Trabaja',default=False)
    domicilio=models.ForeignKey(Domicilio, on_delete=models.PROTECT)
    correo=models.EmailField('e-mail', max_length=100,null=True,blank=True)
    sexo =models.CharField('Sexo', max_length=20,choices=SEXO,blank=False,null=True)
    telefono=models.ForeignKey(Telefono, on_delete=models.PROTECT,null=True)
    horario_disponible=models.ForeignKey(Horario_Disponible, on_delete=models.PROTECT,null=True)
    borrado = models.BooleanField('borrado',default=False)

    def __str__(self):
        return self.nombre + ' ' + self.apellido
    
    def edad(self, fecha_nacimiento):
        diferencia_fechas = date.today() - fecha_nacimiento
        diferencia_fechas_dias = diferencia_fechas.days
        edad_numerica = diferencia_fechas_dias / 365.2425
        edad = int(edad_numerica)
        return edad
    
class Grupo(models.Model):
    id_grupo=models.AutoField(primary_key=True)
    nombre=models.CharField('Nombre', max_length=50,blank=False,null=False)
    miembro=models.ManyToManyField(Miembro)
    borrado = models.BooleanField('borrado',default=False)
    
    def __str__(self):
        return self.nombre
    
class Reunion(models.Model):
    id_reunion=models.AutoField(primary_key=True)
    fecha = models.DateField('Fecha', auto_now=False, auto_now_add=False)
    hora = models.TimeField('Horario', auto_now=False, auto_now_add=False)
    tipo_reunion=models.ForeignKey(Tipo_Reunion, on_delete=models.PROTECT)
    nombre =models.CharField('Nombre', max_length=100,blank=False,null=True)
    domicilio=models.ForeignKey(Domicilio,on_delete=models.PROTECT,blank=False,null=True)
    grupo=models.ForeignKey(Grupo, on_delete=models.PROTECT,null=True)
    borrado = models.BooleanField('borrado',default=False)

    def __str__(self):
        return self.nombre        
    
class Asistencia(models.Model):
    id_asistencia=models.AutoField(primary_key=True)
    presente=models.BooleanField('Presente',default=False)
    justificacion=models.TextField('Justificacion',blank=False,null=True)
    miembro=models.ForeignKey(Miembro, on_delete=models.PROTECT)
    reunion=models.ForeignKey(Reunion, on_delete=models.PROTECT)
        
class Encuesta(models.Model):
    id_fecha_envio=models.AutoField(primary_key=True)
    fecha_envio=models.DateField('Fecha Envio',auto_now=False, auto_now_add=False)
    miembro=models.ForeignKey(Miembro, on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)

class Pregunta(models.Model):
    id_pregunta=models.AutoField(primary_key=True)
    descripcion=models.CharField('Pregunta', max_length=50,blank=False,null=False)
    encuesta=models.ForeignKey(Encuesta, on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)
    
class Respuesta(models.Model):
    id_respuesta=models.AutoField(primary_key=True)
    descripcion=models.CharField('Respuesta', max_length=50,blank=False,null=False)
    puntaje=models.IntegerField('Puntaje')
    pregunta=models.OneToOneField(Pregunta, on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)
    
    



