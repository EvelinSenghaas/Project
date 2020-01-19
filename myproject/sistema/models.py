from django.db import models
from datetime import date
from simple_history.models import HistoricalRecords

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
        return 'calle '+self.calle+'  nro '+self.nro
    
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
    desde=models.TimeField('Desde', auto_now=False, auto_now_add=False,null=True,blank=True)
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
    
class Miembro(models.Model):
    SEXO=[
        ('Masculino','Masculino'),
        ('Femenino','Femenino')
    ]
    dni=models.BigIntegerField('Documento',primary_key=True)
    nombre=models.CharField('Nombre',max_length=200,blank = False, null = False)
    apellido = models.CharField('Apellido',max_length=200,blank = False, null = False)
    fecha_nacimiento = models.DateField('Fecha de Nacimiento', auto_now=False, auto_now_add=False)
    cant_hijo = models.IntegerField('Cantidad de Hijos',null=True)
    trabaja = models.BooleanField('Trabaja',default=False)
    domicilio=models.ForeignKey(Domicilio, on_delete=models.PROTECT)
    correo=models.EmailField('e-mail', max_length=100,null=True,blank=True)
    sexo =models.CharField('Sexo', max_length=20,choices=SEXO,blank=False,null=True)
    telefono=models.ForeignKey(Telefono, on_delete=models.PROTECT,null=True)
    horario_disponible=models.ForeignKey(Horario_Disponible, on_delete=models.PROTECT)
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
    desde=models.IntegerField('Desde',blank=False,null=True)
    hasta=models.IntegerField('Hasta',blank=False,null=True)
    sexo=models.CharField('Sexo', max_length=20,choices=SEXO,blank=False,null=True)
    id_grupo=models.AutoField(primary_key=True)
    nombre=models.CharField('Nombre', max_length=50,blank=False,null=False)
    borrado = models.BooleanField('borrado',default=False)
    miembro=models.ManyToManyField(Miembro)
    encargado=models.IntegerField('Encargado')
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
    justificacion=models.TextField('Justificacion',blank=True,null=True) #Este campo es util si la charla no se dio o si el lider falto
    miembro=models.ForeignKey(Miembro, on_delete=models.PROTECT)
    reunion=models.ForeignKey(Reunion, on_delete=models.PROTECT)
    fecha=models.DateField('Fecha', auto_now=False, auto_now_add=False)
    history = HistoricalRecords()

class Tipo_Pregunta(models.Model):
    id_tipo_pregunta=models.AutoField(primary_key=True)
    tipo=models.CharField('Tipo',max_length=50,blank=False,null=False)
    borrado=models.BooleanField('borrado',default=False)
    history = HistoricalRecords()
    def __str__(self):
        return self.tipo

class Tipo_Encuesta(models.Model):
    id_tipo_encuesta= models.AutoField(primary_key=True)
    tipo=models.CharField("Tipo de Encuesta", max_length=50)
    history = HistoricalRecords()
    def __str__(self):
        return self.tipo

class Encuesta(models.Model):
    ENVIO=[
        ('Semanalmente','Semanalmente'),
        ('Mensualmente','Mensualmente'),
        ('Anualmente','Anualmente')
    ]
    id_encuesta=models.AutoField(primary_key=True)
    envio = models.CharField('Envio',choices=ENVIO,blank=True,null=True, max_length=50)
    borrado = models.BooleanField('borrado',default=False)
    cantidad = models.IntegerField('Cantidad de Faltas',null=True, blank = True)
    reunion=models.ForeignKey(Reunion, on_delete=models.PROTECT)
    tipo=models.OneToOneField(Tipo_Encuesta, on_delete=models.PROTECT,null=True)
    history = HistoricalRecords()

class Pregunta(models.Model):
    id_pregunta=models.AutoField(primary_key=True)
    descripcion=models.CharField('Pregunta', max_length=50,blank=False,null=False)
    borrado = models.BooleanField('borrado',default=False)
    tipo= models.ForeignKey(Tipo_Pregunta, on_delete=models.PROTECT)
    tipo_encuesta=models.OneToOneField(Tipo_Encuesta, on_delete=models.PROTECT,null=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.descripcion    

class Respuesta(models.Model):
    id_respuesta=models.AutoField(primary_key=True)
    descripcion=models.CharField('Respuesta', max_length=50,blank=False,null=False)
    puntaje=models.IntegerField('Puntaje')
    pregunta=models.OneToOneField(Pregunta, on_delete=models.PROTECT)
    borrado = models.BooleanField('borrado',default=False)
    
class Configuracion(models.Model):
    id=models.AutoField(primary_key=True)
    titulo= models.CharField('Titulo', max_length=255,blank=False, null= False)
    telefono = models.CharField('Telefono', max_length=255,blank=False, null= False)
    direccion = models.CharField('Direccion', max_length=255,blank=False, null= False)
    #logo=models.BinaryField('Logo',blank=False,null=False)
    history = HistoricalRecords()

class Estado_Miembro(models.Model):
    id_estado_miembro=models.AutoField(primary_key=True)
    fecha=models.DateField('Fecha', auto_now=False, auto_now_add=False)
    miembro=models.ForeignKey(Miembro, on_delete=models.PROTECT)  
    estado=models.CharField('Estado', max_length=100)

class Estado_Reunion(models.Model):
    id_estado_reunion=models.AutoField(primary_key=True)
    fecha=models.DateField('Fecha', auto_now=False, auto_now_add=False)
    reunion=models.ForeignKey(Reunion, on_delete=models.PROTECT)  
    estado=models.CharField('Estado', max_length=100)
