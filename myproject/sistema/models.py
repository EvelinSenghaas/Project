from django.db import models
from datetime import date
from simple_history.models import HistoricalRecords
from django.core.validators import MinValueValidator

class Tipo_Reunion(models.Model):
    id_tipo_reunion =  models.AutoField(primary_key = True)
    nombre=models.CharField('Nombre',max_length=200,blank = False, null = False)
    descripcion = models.CharField('Descripcion',max_length=200,blank = False, null = True)
    borrado = models.BooleanField('borrado',default=False)
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre 

class Provincia(models.Model):
    id_provincia=models.AutoField(primary_key=True)
    provincia=models.CharField('Provincia', max_length=50,blank=False,null=False)
    borrado = models.BooleanField('borrado',default=False)
    history = HistoricalRecords()
    def __str__(self):
        return self.provincia

class Localidad(models.Model):
    id_localidad = models.AutoField(primary_key = True)
    localidad=models.CharField('Localidad', max_length=50,blank=False,null=False)
    provincia=models.ForeignKey(Provincia,on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)
    history = HistoricalRecords()
    def __str__(self):
        return self.localidad

class Barrio(models.Model):
    id_barrio = models.AutoField(primary_key = True)
    barrio=models.CharField('Barrio', max_length=50,blank=False,null=False)
    localidad=models.ForeignKey(Localidad, on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)
    history = HistoricalRecords()
    def __str__(self):
        return self.barrio

class Domicilio(models.Model):
    id_domicilio = models.AutoField(primary_key=True)
    calle=models.CharField('Calle', max_length=100,blank=False,null=False)
    nro=models.CharField('Numero', max_length=50,blank=False,null=False)
    mz = models.CharField('Manzana', max_length=50,null=True,blank=True)
    departamento=models.CharField('Departamento', max_length=50,null=True,blank=True)
    piso=models.CharField('Piso', max_length=50,null=True,blank=True)
    barrio=models.ForeignKey(Barrio, on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)
    
    def __str__(self):
        return 'calle '+self.calle+'  nro '
    
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
    dia=models.CharField('dia',max_length=50,blank=True,null=True,choices=DIA)
    desde=models.TimeField('Desd e', auto_now=False, auto_now_add=False,null=True,blank=True)
    hasta=models.TimeField('Hasta', auto_now=False, auto_now_add=False,null=True,blank=True)
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
    tipo=models.CharField('Tipo', max_length=50,blank=True,null=True,choices=TIPO)
    empresa=models.CharField('Empresa', max_length=50,blank=True,null=True,choices=EMPRESA)
    borrado = models.BooleanField('borrado',default=False)

    
    def __str__(self):
        return self.tipo
    
class Telefono(models.Model):
    id_telefono=models.AutoField(primary_key=True)
    prefijo=models.IntegerField('Prefijo',blank=True,null=True)
    numero=models.IntegerField('Numero',null=True,blank=True)
    whatsapp=models.BooleanField('Whatsapp',default=True)
    tipo_telefono=models.ForeignKey(Tipo_Telefono, on_delete=models.PROTECT,null=True)
    borrado = models.BooleanField('borrado',default=False)    
    # miembro no def :C contacto= models.ForeignKey(Miembro, on_delete=models.PROTECT,null=True) #tel de contacto en caso de necesitar
    def __str__(self):
        return 'naranja'

class Estado_Civil(models.Model):
    id_estado = models.AutoField(primary_key=True)
    estado= models.CharField('soltero/a', max_length=20,blank=False, null=False)
    def __str__(self):
        return self.estado
    
class Miembro(models.Model):
    class Meta:
        unique_together = (('dni', 'sexo'),)
    SEXO=[
        ('Masculino','Masculino'),
        ('Femenino','Femenino')
    ]
    dni=models.BigIntegerField('Documento',primary_key=True)
    nombre=models.CharField('Nombre',max_length=200,blank = False, null = False)
    apellido = models.CharField('Apellido',max_length=200,blank = False, null = False)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', auto_now=False, auto_now_add=False)
    cant_hijo = models.IntegerField('Cantidad de Hijos',null=True,validators=[MinValueValidator(0)])
    trabaja = models.BooleanField('Trabaja',default=False)
    domicilio=models.ForeignKey(Domicilio, on_delete=models.PROTECT)
    correo=models.EmailField('e-mail', max_length=100,null=True,blank=True)
    sexo =models.CharField('Sexo', max_length=20,choices=SEXO,blank=False,null=True)
    telefono=models.ForeignKey(Telefono, on_delete=models.PROTECT,null=True)
    horario_disponible=models.ManyToManyField(Horario_Disponible)
    borrado = models.BooleanField('borrado',default=False)
    estado_civil=models.ForeignKey(Estado_Civil, on_delete=models.PROTECT)
    history = HistoricalRecords()


    def __str__(self):
        return self.nombre + ' ' + self.apellido
    
    def edad(self, fecha_nacimiento):
        diferencia_fechas = date.today() - fecha_nacimiento
        diferencia_fechas_dias = diferencia_fechas.days
        edad_numerica = diferencia_fechas_dias / 365.2425
        edad = int(edad_numerica)
        return edad

class Telefono_Contacto(models.Model):
    id=models.AutoField(primary_key=True)
    miembro=models.ForeignKey(Miembro, on_delete=models.PROTECT)

class Grupo(models.Model):
    SEXO=[
        ('Masculino','Masculino'),
        ('Femenino','Femenino'),
        ('Ambos','Ambos')
    ]
    desde=models.IntegerField('Desde',blank=False,null=True,validators=[MinValueValidator(0)])
    hasta=models.IntegerField('Hasta',blank=False,null=True,validators=[MinValueValidator(0)])
    sexo=models.CharField('Sexo', max_length=20,choices=SEXO,blank=False,null=True)
    id_grupo=models.AutoField(primary_key=True)
    nombre=models.CharField('Nombre', max_length=50,blank=False,null=False)
    borrado = models.BooleanField('borrado',default=False)
    miembro=models.ManyToManyField(Miembro)
    encargado=models.IntegerField('Encargado')#aca guardo el id del usuario encargado
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre

class Reunion(models.Model):
    id_reunion=models.AutoField(primary_key=True)
    tipo_reunion=models.ForeignKey(Tipo_Reunion, on_delete=models.PROTECT)
    nombre =models.CharField('Nombre', max_length=100,blank=False,null=True)
    domicilio=models.ForeignKey(Domicilio,on_delete=models.PROTECT,blank=False,null=True)
    grupo=models.ForeignKey(Grupo, on_delete=models.PROTECT,null=True)
    borrado = models.BooleanField('borrado',default=False)
    horario= models.ForeignKey(Horario_Disponible, on_delete=models.CASCADE,blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre        
    
class Asistencia(models.Model):
    id_asistencia=models.AutoField(primary_key=True)
    presente=models.BooleanField('Presente',default=False,null=True,blank=True)
    #creo que justificaciones tiene que ir aparte jiji
    miembro=models.ForeignKey(Miembro, on_delete=models.PROTECT)
    reunion=models.ForeignKey(Reunion, on_delete=models.PROTECT)
    fecha=models.DateField('Fecha', auto_now=False, auto_now_add=False)
    history = HistoricalRecords()
    justificado=models.BooleanField(null=True)

class Tipo_Pregunta(models.Model):
    id_tipo_pregunta=models.AutoField(primary_key=True)
    tipo=models.CharField('Tipo',max_length=50,blank=False,null=False)
    borrado=models.BooleanField('borrado',default=False)
    history = HistoricalRecords()
    def __str__(self):
        return self.tipo

class Pregunta(models.Model):
    id_pregunta=models.AutoField(primary_key=True)
    descripcion=models.CharField('Pregunta', max_length=200,blank=False,null=False)
    borrado = models.BooleanField('borrado',default=False,null=True)
    tipo= models.ForeignKey(Tipo_Pregunta, on_delete=models.PROTECT)
    history = HistoricalRecords()

    def __str__(self):
        return self.descripcion  

class Tipo_Encuesta(models.Model):
    id_tipo_encuesta= models.AutoField(primary_key=True)
    tipo=models.CharField("Tipo de Encuesta", max_length=50)
    cantidad = models.IntegerField('Cantidad de Faltas',null=True, blank = True)
    preguntas=models.ManyToManyField(Pregunta)
    def __str__(self):
        return self.tipo

class Encuesta(models.Model):
    id_encuesta=models.AutoField(primary_key=True)
    borrado = models.BooleanField('borrado',default=False)
    reunion=models.ForeignKey(Reunion, on_delete=models.PROTECT,null=True)
    tipo=models.ForeignKey(Tipo_Encuesta, on_delete=models.PROTECT,null=True)
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE,null=True)
    fecha_envio=models.DateField( auto_now=False, auto_now_add=False)
    fecha_respuesta=models.DateField( auto_now=False, auto_now_add=False,null=True)
    puntaje=models.IntegerField(null=True)
    respondio=models.BooleanField(null=True)
    history = HistoricalRecords()

class Opciones(models.Model):
    id=models.AutoField(primary_key=True)
    pregunta=models.ForeignKey(Pregunta, on_delete=models.PROTECT)
    opcion=models.CharField(max_length=150,null=True)
    puntaje=models.IntegerField()
    borrado=models.BooleanField(default=False)
    def __str__(self):
        return self.opcion 

class Respuesta(models.Model):
    id_respuesta=models.AutoField(primary_key=True)
    pregunta=models.ForeignKey(Pregunta, on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)
    encuesta=models.ForeignKey(Encuesta, on_delete=models.PROTECT)
    opcion=models.ForeignKey(Opciones,on_delete=models.PROTECT)
    
class Configuracion(models.Model):
    id=models.AutoField(primary_key=True)
    titulo= models.CharField('Titulo', max_length=255,blank=False, null= False)
    telefono = models.CharField('Telefono', max_length=255,blank=False, null= False)
    direccion = models.CharField('Direccion', max_length=255,blank=False, null= False)
    #logo=models.BinaryField('Logo',blank=False,null=False)
    history = HistoricalRecords()

class Permisos(models.Model):
    id_permiso=models.AutoField(primary_key=True)
    nombre=models.CharField('Permiso', max_length=100)

class Rol(models.Model):
    id_rol=models.AutoField(primary_key=True)
    nombre=models.CharField("Nombre", max_length=50)
    permisos=models.ManyToManyField(Permisos)
    borrado=models.BooleanField(default=False)
    def __str__(self):
        return self.nombre

class Estado_Reunion(models.Model):
    id = models.AutoField(primary_key=True)
    reunion=models.ForeignKey(Reunion, on_delete=models.PROTECT)
    estado=models.CharField(max_length=50)
    fecha=models.DateField( auto_now_add=True)
    encuesta=models.OneToOneField(Encuesta, on_delete=models.PROTECT)