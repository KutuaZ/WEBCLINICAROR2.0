# core/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Sede(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Medico(models.Model):
    TIPO_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('TELEMEDICINA', 'Telemedicina'),
        ('LABORATORIO', 'Laboratorio'),
    ]
    # El campo 'nombre' en User (first_name) será el nombre del médico.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True, blank=True)
    sede = models.ForeignKey(Sede, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='PRESENCIAL') # <-- AÑADIR ESTA LÍNEA


    def __str__(self):
        # El __str__ ahora maneja los campos opcionales
        especialidad_info = f" ({self.especialidad.nombre})" if self.especialidad else ""
        sede_info = f" - {self.sede.nombre}" if self.sede else ""
        return f"{self.user.get_full_name()}{especialidad_info} ({self.get_tipo_display()}{sede_info})"


class HoraDisponible(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='horas_disponibles')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medico.user.get_full_name()} - {self.fecha.strftime('%d-%m-%Y')} de {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"

    class Meta:
        unique_together = ('medico', 'fecha', 'hora_inicio')
        ordering = ['fecha', 'hora_inicio'] # Ordena las horas cronológicamente

class Reserva(models.Model):
    # Campos para el paciente que reserva (no necesita estar logueado)
    nombre_paciente = models.CharField(max_length=100)
    email_paciente = models.EmailField()
    telefono_paciente = models.CharField(max_length=20)
    rut_paciente = models.CharField(max_length=20)
    
    # Relación con el médico y la hora
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    
    # asegurar que una hora solo se pueda reservar una vez.
    hora_disponible = models.OneToOneField(HoraDisponible, on_delete=models.CASCADE)
    
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reserva de {self.nombre_paciente} con Dr. {self.medico.user.get_full_name()} el {self.hora_disponible.fecha}"
    
class Paciente(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='paciente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rut = models.CharField(max_length=20, unique=True, null=True, blank=True)   
    
    def __str__(self):
        return self.user.get_full_name()
    

class HistorialMedico(models.Model):

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    descripcion = models.TextField("Detalle de la atención")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Usamos el nombre de la reserva para evitar errores si no hay un paciente
        return f"Historial para la reserva de {self.reserva.nombre_paciente} - {self.fecha.date()}"


class Ticket(models.Model):
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=100)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Ticket de {self.nombre_completo} - {self.asunto}"
    
    
    
# --- MODELOS PARA LA FARMACIA ---

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class Orden(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Completado', 'Completado'),
        ('Cancelado', 'Cancelado'),
    ]
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    nombre_completo = models.CharField(max_length=100, default='')
    direccion = models.CharField(max_length=255, default='')
    ciudad = models.CharField(max_length=100, default='')
    telefono = models.CharField(max_length=20, default='')
    def __str__(self):
        return f"Orden #{self.id} - {self.usuario.username if self.usuario else 'Invitado'}"

class OrdenProducto(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2) # Precio al momento de la compra

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Orden #{self.orden.id}"
    
    
class Arancel(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class Cuenta(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='cuentas')
    concepto = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=0)
    fecha_emision = models.DateField(auto_now_add=True)
    pagado = models.BooleanField(default=False)

    def __str__(self):
        return f"Deuda de {self.paciente.user.get_full_name()} por {self.concepto}"
    

class ResultadoLaboratorio(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='resultados')
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, null=True, blank=True)
    titulo_examen = models.CharField(max_length=255)
    archivo_resultado = models.FileField(upload_to='resultados_laboratorio/')
    fecha_subido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado de {self.titulo_examen} for {self.paciente.user.get_full_name()}"