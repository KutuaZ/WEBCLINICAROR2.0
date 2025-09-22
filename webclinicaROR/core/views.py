from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from .models import (Paciente, Especialidad, Sede, Medico, HoraDisponible, Reserva, HistorialMedico, HistorialMedico, Ticket, Producto, Orden)
from datetime import datetime, timedelta
from django.utils import timezone
from .forms import ReservaForm, TicketForm, ProductoForm
from django.db import transaction



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
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu mensaje ha sido enviado! Te responderemos a la brevedad.')
            return redirect('contacto')
    else:
        form = TicketForm()
    return render(request, 'paginasinicio/contacto.html', {'form': form})

def farmacia_estatico(request):
    productos = Producto.objects.all() # Obtener todos los productos
    return render(request, 'paginasinicio/farmacia.html', {'productos': productos})

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

def historial_paciente(request, paciente_id):
    from .models import HistorialMedico, Paciente  # Importar aquí para evitar ciclos

    paciente = get_object_or_404(Paciente, id=paciente_id)
    historiales = HistorialMedico.objects.filter(paciente=paciente).select_related('medico', 'reserva')

    return render(request, 'paginasenlace/historial_paciente.html', {'paciente': paciente, 'historiales': historiales})

@login_required
def agregar_historial(request, reserva_id):
    from .models import HistorialMedico, Reserva  # Importar aquí para evitar ciclos

    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        if descripcion:
            HistorialMedico.objects.create(
                paciente=reserva.paciente,
                medico=reserva.medico,
                reserva=reserva,
                descripcion=descripcion
            )
            messages.success(request, 'Historial médico agregado con éxito.')
            return redirect('historial_paciente', paciente_id=reserva.paciente.id)
        else:
            messages.error(request, 'La descripción no puede estar vacía.')

    return render(request, 'paginasenlace/agregar_historial.html', {'reserva': reserva})


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



def registro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        rut = request.POST.get("rut", "").strip()
        password = request.POST.get("password")
        confirmar = request.POST.get("confirmar")

        # --- VALIDACIONES (Estas ya estaban bien) ---
        if not all([nombre, email, telefono, rut, password, confirmar]):
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect("registro")

        if password != confirmar:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("registro")

        if User.objects.filter(username=email).exists():
            messages.error(request, "El correo electrónico ya está registrado.")
            return redirect("registro")
        
        if Paciente.objects.filter(rut=rut).exists():
            messages.error(request, "El RUT ya está registrado.")
            return redirect("registro")

        try:
            with transaction.atomic():
                #  Crear el usuario
                user = User.objects.create_user(username=email, email=email, password=password)
                user.first_name = nombre
                user.save()

                #  Busca el grupo 'paciente'. Si no existe, lo crea.
                grupo_paciente, created = Group.objects.get_or_create(name='paciente')
                user.groups.add(grupo_paciente)

                #  Crear el perfil del Paciente
                Paciente.objects.create(user=user, telefono=telefono, rut=rut)

            messages.success(request, "¡Registro completado con éxito! Ahora puedes iniciar sesión.")
            return redirect("iniciarsesion")

        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {e}")
            return redirect("registro")

    return render(request, "paginasenlace/registro.html")



def vista_reserva(request):
    # Obtener datos para los select
    sedes = Sede.objects.all()
    especialidades = Especialidad.objects.all()
    medicos = Medico.objects.select_related('user', 'especialidad', 'sede').all()
    horas = HoraDisponible.objects.filter(disponible=True).select_related('medico')

    if request.method == 'POST':
        form = ReservaForm(request.POST)

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

@login_required
def agenda_estatico(request):
    reservas = []
    try:
        medico = Medico.objects.get(user=request.user)
        reservas = Reserva.objects.filter(medico=medico).select_related('hora_disponible')
    except Medico.DoesNotExist:
        pass  # El usuario no es médico, no se muestran reservas

    return render(request, 'paginasenlace/agenda.html', {'reservas': reservas})



@login_required
def historial_paciente_rut(request, rut):
    # Solo los médicos pueden ver esta página
    if not hasattr(request.user, 'medico'):
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')

    medico_actual = request.user.medico

    if request.method == 'POST':
        reserva_id = request.POST.get('reserva_id')
        descripcion = request.POST.get('descripcion')
        
        if reserva_id and descripcion:
            reserva = get_object_or_404(Reserva, id=reserva_id)

            if reserva.medico == medico_actual:
                
                # Busca al paciente por el RUT de la reserva. Si no lo encuentra, no hay problema.
                paciente_obj = Paciente.objects.filter(rut=reserva.rut_paciente).first()

                HistorialMedico.objects.create(
                    paciente=paciente_obj, 
                    medico=medico_actual,
                    reserva=reserva,
                    descripcion=descripcion
                )
                messages.success(request, "Historial agregado con éxito.")
            else:
                messages.error(request, "No tienes permiso para modificar esta reserva.")
        else:
            messages.error(request, "Faltan datos para agregar el historial.")
        
        return redirect('historial_paciente_rut', rut=rut)

    reservas = Reserva.objects.filter(rut_paciente=rut).select_related(
        'medico__user', 
        'medico__especialidad', 
        'hora_disponible'
    ).prefetch_related('historialmedico_set__medico__user').order_by('-hora_disponible__fecha')

    context = {
        'reservas': reservas,
        'nombre_paciente': reservas.first().nombre_paciente if reservas else "Desconocido",
        'rut_paciente': rut,
    }
    return render(request, 'paginasenlace/historial_paciente.html', context)


@login_required
def historial_personal(request):
    try:
        # Se busca al paciente asociado al usuario que ha iniciado sesión
        paciente = Paciente.objects.get(user=request.user)
        
        # Se obtienen todos los historiales médicos asociados a ese paciente
        historiales = HistorialMedico.objects.filter(paciente=paciente).order_by('-reserva__hora_disponible__fecha')
        
        context = {
            'historiales': historiales,
            'nombre_paciente': f"{paciente.user.first_name} {paciente.user.last_name}",
            'rut_paciente': paciente.rut,
        }
        
        # Se renderiza la plantilla correcta con el contexto
        return render(request, 'paginasenlace/historial_personal.html', context)

    except Paciente.DoesNotExist:
        
        messages.error(request, 'No se encontró un perfil de paciente asociado a su cuenta.')
        return redirect('index')
    
    

# Vistas de administración para admin-web
@login_required
def admin_tickets(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    tickets = Ticket.objects.all().order_by('-fecha_creacion')
    return render(request, 'paginasenlace/admin_tickets.html', {'tickets': tickets})

@login_required
def admin_farmacia(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    productos = Producto.objects.all()
    return render(request, 'paginasenlace/admin_farmacia.html', {'productos': productos})

@login_required
def admin_producto_crear(request):
    if not request.user.groups.filter(name='admin-web').exists():
        return redirect('index')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto añadido correctamente.')
            return redirect('admin_farmacia')
    else:
        form = ProductoForm()
    
    return render(request, 'paginasenlace/admin_producto_form.html', {'form': form})

@login_required
def admin_producto_editar(request, producto_id):
    if not request.user.groups.filter(name='admin-web').exists():
        return redirect('index')
    
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('admin_farmacia')
    else:
        form = ProductoForm(instance=producto)
        
    return render(request, 'paginasenlace/admin_producto_form.html', {'form': form, 'producto': producto})

@login_required
def admin_producto_eliminar(request, producto_id):
    if not request.user.groups.filter(name='admin-web').exists():
        return redirect('index')
    
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect('admin_farmacia')



@login_required
def admin_pagos(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    # Lógica para administrar pagos
    return render(request, 'paginasenlace/admin_pagos.html')

@login_required
def admin_aranceles(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    # Lógica para administrar aranceles
    return render(request, 'paginasenlace/admin_aranceles.html')