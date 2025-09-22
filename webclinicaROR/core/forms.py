# core/forms.py

from django import forms
import re
from .models import Ticket, Producto, Orden, Arancel, Cuenta

class ReservaForm(forms.Form):
    # Definimos widgets para añadir clases de CSS y atributos de HTML
    nombre_paciente = forms.CharField(label='Nombre Completo', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Juan Pérez'}
    ))
    email_paciente = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}
    ))
    telefono_paciente = forms.CharField(label='Teléfono', max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}
    ))
    rut_paciente = forms.CharField(label='RUT', max_length=12, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}
    ))

    
    sede = forms.ChoiceField(label='Sede', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    especialidad = forms.ChoiceField(label='Especialidad', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    medico = forms.ChoiceField(label='Médico', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    hora = forms.ChoiceField(label='Hora de la Cita', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))

    # --- VALIDACIONES 
    def clean_rut_paciente(self):
        rut = self.cleaned_data['rut_paciente']
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise forms.ValidationError("El formato del RUT debe ser XX.XXX.XXX-X.")
        return rut
    
    def clean_telefono_paciente(self):
        telefono = self.cleaned_data['telefono_paciente']
        telefono_limpio = telefono.replace(" ", "").replace("+", "")
        if not telefono_limpio.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números.")
        return telefono
    
    

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['nombre_completo', 'email', 'asunto', 'mensaje']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Juan Pérez', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'correo@ejemplo.com', 'required': True}),
            'asunto': forms.Select(attrs={'class': 'form-select form-select-lg', 'required': True}, choices=[
                ('', 'Selecciona un asunto'),
                ('trabajo', 'Busco trabajo'),
                ('practica', 'Busco práctica profesional'),
                ('alianza', 'Busco alianza o convenio'),
                ('reclamo', 'Reclamo'),
            ]),
            'mensaje': forms.Textarea(attrs={'class': 'form-control form-control-lg', 'rows': 5, 'placeholder': 'Escribe tu mensaje aquí...', 'required': True}),
        }
        

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['nombre_completo', 'direccion', 'ciudad', 'telefono']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Completo'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Siempreviva 742'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Santiago'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56 9 1234 5678'}),
        }

class ArancelForm(forms.ModelForm):
    class Meta:
        model = Arancel
        fields = ['codigo', 'nombre', 'precio']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['paciente', 'concepto', 'monto', 'pagado']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'concepto': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_concepto'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_monto'}),
            'pagado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        

class ReservaLabForm(forms.Form):
    nombre_paciente = forms.CharField(label='Nombre Completo', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Juan Pérez'}
    ))
    email_paciente = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}
    ))
    telefono_paciente = forms.CharField(label='Teléfono', max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}
    ))
    rut_paciente = forms.CharField(label='RUT', max_length=12, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}
    ))
    hora = forms.ChoiceField(label='Hora de la Cita', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))


class ReservaOnlineForm(forms.Form):
    # Hereda los campos y validaciones que sí necesitamos
    nombre_paciente = forms.CharField(label='Nombre Completo', max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Juan Pérez'}
    ))
    email_paciente = forms.EmailField(label='Correo Electrónico', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}
    ))
    telefono_paciente = forms.CharField(label='Teléfono', max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}
    ))
    rut_paciente = forms.CharField(label='RUT', max_length=12, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}
    ))
    # Campos específicos para esta vista
    medico = forms.ChoiceField(label='Médico', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    hora = forms.ChoiceField(label='Hora de la Cita', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))

    def clean_rut_paciente(self):
        rut = self.cleaned_data['rut_paciente']
        if not re.match(r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$', rut):
            raise forms.ValidationError("El formato del RUT debe ser XX.XXX.XXX-X.")
        return rut
    
    def clean_telefono_paciente(self):
        telefono = self.cleaned_data['telefono_paciente']
        telefono_limpio = telefono.replace(" ", "").replace("+", "")
        if not telefono_limpio.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números.")
        return telefono