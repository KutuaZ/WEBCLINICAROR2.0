from django.contrib import admin
from .models import (
    Especialidad, Sede, Medico, HoraDisponible, Reserva, Ticket, 
    Producto, Orden, OrdenProducto, ResultadoLaboratorio
)

class MedicoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'especialidad', 'sede', 'tipo') 
    list_filter = ('tipo', 'sede', 'especialidad') 
    search_fields = ('user__first_name', 'user__last_name', 'especialidad__nombre')

class HoraDisponibleAdmin(admin.ModelAdmin):
    list_display = ('medico', 'fecha', 'hora_inicio', 'hora_fin', 'disponible')
    list_filter = ('disponible', 'medico__tipo', 'medico', 'fecha') 
    search_fields = ('medico__user__first_name', 'fecha')

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('nombre_paciente', 'medico', 'get_fecha', 'get_hora_inicio')
    list_filter = ('medico__tipo', 'medico', 'hora_disponible__fecha') 
    search_fields = ('nombre_paciente', 'rut_paciente', 'medico__user__first_name')

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

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock')
    search_fields = ('nombre',)

class OrdenProductoInline(admin.TabularInline):
    model = OrdenProducto
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio')

class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_creacion', 'total', 'estado')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('usuario__username', 'id')
    inlines = [OrdenProductoInline]

class ResultadoLaboratorioAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'titulo_examen', 'fecha_subido')
    search_fields = ('paciente__user__first_name', 'paciente__rut', 'titulo_examen')

# Registros
admin.site.register(Especialidad)
admin.site.register(Sede)
admin.site.register(Medico, MedicoAdmin)
admin.site.register(HoraDisponible, HoraDisponibleAdmin)
admin.site.register(Reserva, ReservaAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Orden, OrdenAdmin)
admin.site.register(ResultadoLaboratorio, ResultadoLaboratorioAdmin) 