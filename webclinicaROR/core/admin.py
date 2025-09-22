from django.contrib import admin
from .models import Especialidad, Sede, Medico, HoraDisponible, Reserva, Ticket
# Register your models here.


class MedicoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'especialidad', 'sede')
    search_fields = ('user__first_name', 'user__last_name', 'especialidad__nombre')

class HoraDisponibleAdmin(admin.ModelAdmin):
    list_display = ('medico', 'fecha', 'hora_inicio', 'hora_fin', 'disponible')
    list_filter = ('disponible', 'medico', 'fecha')
    search_fields = ('medico__user__first_name', 'fecha')

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre_paciente', 'medico', 'get_fecha', 'get_hora_inicio')
    list_filter = ('medico', 'hora_disponible__fecha')
    search_fields = ('nombre_paciente', 'rut_paciente', 'medico__user__first_name')

    # Funciones para mostrar datos de la hora relacionada
    def get_fecha(self, obj):
        return obj.hora_disponible.fecha
    get_fecha.short_description = 'Fecha'

    def get_hora_inicio(self, obj):
        return obj.hora_disponible.hora_inicio
    get_hora_inicio.short_description = 'Hora de Inicio'
    
    
class TicketAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'asunto', 'fecha_creacion', 'leido')
    list_filter = ('leido', 'asunto')
    search_fields = ('nombre_completo', 'email', 'mensaje')

admin.site.register(Especialidad)
admin.site.register(Sede)
admin.site.register(Medico, MedicoAdmin)
admin.site.register(HoraDisponible, HoraDisponibleAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Ticket, TicketAdmin)