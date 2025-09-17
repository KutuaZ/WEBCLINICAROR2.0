# core/forms.py

from django import forms
import re

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

    # Dejamos los ChoiceFields sin datos, ya que se llenan dinámicamente
    sede = forms.ChoiceField(label='Sede', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    especialidad = forms.ChoiceField(label='Especialidad', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    medico = forms.ChoiceField(label='Médico', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
    hora = forms.ChoiceField(label='Hora de la Cita', choices=[], widget=forms.Select(attrs={'class': 'form-select'}))

    # --- VALIDACIONES PERSONALIZADAS (sin cambios) ---
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