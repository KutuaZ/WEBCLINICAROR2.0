from rest_framework import serializers
from .models import Especialidad, Sede, Medico, HoraDisponible, Reserva, Ticket, Producto, Orden, OrdenProducto, Arancel, Cuenta, ResultadoLaboratorio, Paciente, HistorialMedico


class especialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['id', 'nombre']

class sedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ['id', 'nombre']
        
class medicoSerializer(serializers.ModelSerializer):
    especialidad = especialidadSerializer(read_only=True)
    sede = sedeSerializer(read_only=True)
    
    class Meta:
        model = Medico
        fields = ['id', 'user', 'especialidad', 'sede', 'tipo']

class horaDisponibleSerializer(serializers.ModelSerializer):
    medico = medicoSerializer(read_only=True)
    
    class Meta:
        model = HoraDisponible
        fields = ['id', 'medico', 'fecha', 'hora_inicio', 'hora_fin', 'disponible']
        
class reservaSerializer(serializers.ModelSerializer):
    medico = medicoSerializer(read_only=True)
    
    class Meta:
        model = Reserva
        fields = ['id', 'nombre_paciente', 'email_paciente', 'telefono_paciente', 'rut_paciente', 'medico', 'hora_disponible', 'fecha_creacion']
        
class pacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ['id', 'user', 'telefono', 'rut']

class historialMedicoSerializer(serializers.ModelSerializer):
    medico = medicoSerializer(read_only=True)
    paciente = pacienteSerializer(read_only=True)
    
    class Meta:
        model = HistorialMedico
        fields = ['id', 'medico', 'paciente', 'reserva', 'fecha', 'descripcion']
        
class ticketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'nombre_completo', 'email', 'asunto', 'mensaje', 'leido', 'fecha_creacion']

class productoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'imagen']

class ordenSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Orden
        fields = ['id', 'usuario', 'fecha_creacion', 'total', 'estado', 'nombre_completo', 'direccion', 'ciudad', 'telefono']

class ordenProductoSerializer(serializers.ModelSerializer):
    producto = productoSerializer(read_only=True)
    orden = ordenSerializer(read_only=True)
    
    class Meta:
        model = OrdenProducto
        fields = ['id', 'orden', 'producto', 'cantidad', 'precio']

class arancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arancel
        fields = ['id', 'nombre', 'codigo', 'precio']

class cuentaSerializer(serializers.ModelSerializer):
    paciente = pacienteSerializer(read_only=True)
    
    class Meta:
        model = Cuenta
        fields = ['id', 'paciente', 'concepto', 'fecha_emision', 'monto', 'pagado']

class resultadoLaboratorioSerializer(serializers.ModelSerializer):
    paciente = pacienteSerializer(read_only=True)
    
    class Meta:
        model = ResultadoLaboratorio
        fields = ['id', 'paciente', 'reserva', 'titulo_examen', 'archivo_resultado', 'fecha_subido']
