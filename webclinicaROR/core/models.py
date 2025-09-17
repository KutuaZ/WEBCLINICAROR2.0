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
    # El campo 'nombre' en User (first_name) será el nombre del médico.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

    def __str__(self):
        # Usamos el nombre del modelo User para evitar redundancia
        return f"{self.user.get_full_name()} ({self.especialidad.nombre})"

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
    
    # Usamos OneToOneField para asegurar que una hora solo se pueda reservar una vez.
    hora_disponible = models.OneToOneField(HoraDisponible, on_delete=models.CASCADE)
    
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Reserva de {self.nombre_paciente} con Dr. {self.medico.user.get_full_name()} el {self.hora_disponible.fecha}"