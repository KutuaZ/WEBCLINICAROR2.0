from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Especialidad, Sede, Medico, HoraDisponible, Reserva
from datetime import datetime, timedelta
from django.utils import timezone
from .forms import ReservaForm
# Páginas estáticas
def index_estatico(request):
    return render(request, 'paginasinicio/index.html')

#def formulario_reserva(request):
    #return render(request, 'paginasinicio/reserva.html')#

def especialidades_estatico(request):
    return render(request, 'paginasinicio/especialidades.html')

def nosotros_estatico(request):
    return render(request, 'paginasinicio/nosotros.html')

def formulario_contacto(request):
    return render(request, 'paginasinicio/contacto.html')

def farmacia_estatico(request):
    return render(request, 'paginasinicio/farmacia.html')

def formulario_reservalab(request):
    return render(request, 'paginasenlace/reservalab.html')

def formulario_reservaonline(request):
    return render(request, 'paginasenlace/reservaonline.html')

def aranceles_estatico(request):
    return render(request, 'paginasenlace/aranceles.html')

def seguros_estatico(request):
    return render(request, 'paginasenlace/seguros.html')

def formulario_pagocuentas(request):
    return render(request, 'paginasenlace/pagocuentas.html')

def formulario_soporte(request):
    return render(request, 'paginasenlace/soporte.html')

def preguntas_estatico(request):
    return render(request, 'paginasenlace/preguntas.html')

def agenda_medico(request):
    return render(request, 'paginasenlace/agenda.html')

# Login
def iniciar_sesion(request):
    if request.method == "POST":
        email_or_username = request.POST.get("email")
        password = request.POST.get("password")

        # Buscar por email o username, tomar el primero si hay duplicados
        user_qs = User.objects.filter(email=email_or_username) | User.objects.filter(username=email_or_username)
        user_obj = user_qs.first()

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Usuario o contraseña incorrectos")
        else:
            messages.error(request, "Usuario no encontrado")

    return render(request, "paginasinicio/iniciarsesion.html", {"email": request.POST.get("email", "")})

# Logout
def cerrar_sesion(request):
    logout(request)
    return redirect("index")

# Registro
def registro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        email = request.POST.get("email")
        password = request.POST.get("password")
        tipo_usuario = request.POST.get("tipo_usuario")  # paciente, med, admin-web

        if User.objects.filter(username=email).exists():
            messages.error(request, "El usuario ya existe")
            return redirect("registro")

        user = User.objects.create_user(username=email, email=email, password=password, first_name=nombre)

        if tipo_usuario:
            group, _ = Group.objects.get_or_create(name=tipo_usuario)
            user.groups.add(group)

        user.save()
        messages.success(request, "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
        return redirect("iniciarsesion")

    return render(request, "paginasenlace/registro.html")


def vista_reserva(request):
    # Definimos los querysets fuera para usarlos en GET y POST
    sedes = Sede.objects.all()
    especialidades = Especialidad.objects.all()
    medicos = Medico.objects.select_related('user', 'especialidad', 'sede').all()
    horas = HoraDisponible.objects.filter(disponible=True).select_related('medico')

    if request.method == 'POST':
        form = ReservaForm(request.POST)

        # --- ESTA ES LA PARTE CLAVE DE LA SOLUCIÓN ---
        # Le damos al formulario la lista de opciones válidas ANTES de llamar a is_valid()
        form.fields['sede'].choices = [(sede.id, sede.nombre) for sede in sedes]
        form.fields['especialidad'].choices = [(esp.id, esp.nombre) for esp in especialidades]
        form.fields['medico'].choices = [(medico.id, medico.user.get_full_name()) for medico in medicos]
        form.fields['hora'].choices = [(hora.id, f"{hora.hora_inicio.strftime('%H:%M')} - {hora.hora_fin.strftime('%H:%M')}") for hora in horas]
        
        if form.is_valid():
            datos = form.cleaned_data
            
            try:
                hora_obj = HoraDisponible.objects.get(id=datos['hora'], disponible=True)
                medico_obj = Medico.objects.get(id=datos['medico'])

                Reserva.objects.create(
                    nombre_paciente=datos['nombre_paciente'],
                    email_paciente=datos['email_paciente'],
                    telefono_paciente=datos['telefono_paciente'],
                    rut_paciente=datos['rut_paciente'],
                    medico=medico_obj,
                    hora_disponible=hora_obj
                )

                hora_obj.disponible = False
                hora_obj.save()

                messages.success(request, '¡Tu hora ha sido reservada con éxito!')
                return redirect('reserva')

            except (HoraDisponible.DoesNotExist, Medico.DoesNotExist):
                messages.error(request, 'La hora o el médico seleccionados ya no son válidos.')
                return redirect('reserva')
    
    else: # Si es un GET
        form = ReservaForm()

    context = {
        'form': form,
        'sedes': sedes,
        'especialidades': especialidades,
        'medicos': medicos,
        'horas': horas,
    }
    return render(request, 'paginasinicio/reserva.html', context)