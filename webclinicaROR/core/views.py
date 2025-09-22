from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from .models import (Paciente, Especialidad, Sede, Medico, HoraDisponible, Reserva, HistorialMedico, HistorialMedico, Ticket, Producto, Orden, OrdenProducto)
from datetime import datetime, timedelta
from django.utils import timezone
from .forms import ReservaForm, TicketForm, ProductoForm, CheckoutForm
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST



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


@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    
    # Si el producto ya está en el carrito, aumentamos la cantidad
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        # Si no, lo agregamos
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': int(producto.precio),
            'cantidad': 1,
            'imagen': producto.imagen.url if producto.imagen else ''
        }
    
    request.session['carrito'] = carrito
    return JsonResponse({'mensaje': 'Producto agregado al carrito'})

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    items = []
    total = 0
    for id, detalles in carrito.items():
        subtotal = detalles['precio'] * detalles['cantidad']
        total += subtotal
        items.append({
            'id': id,
            'nombre': detalles['nombre'],
            'precio': detalles['precio'],
            'cantidad': detalles['cantidad'],
            'imagen': detalles['imagen'],
            'subtotal': subtotal
        })
    form = CheckoutForm()
    return render(request, 'paginasenlace/carrito.html', {'items': items, 'total': total})


@require_POST
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')

@login_required
@require_POST # Nos aseguramos que esta vista solo acepte peticiones POST
def procesar_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('farmacia')

    # Procesamos el formulario con los datos del POST
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        # Si el formulario no es válido, volvemos al carrito mostrando los errores
        messages.error(request, 'Por favor, completa correctamente los datos de envío.')
        # Re-renderizamos la página del carrito con los errores
        # (necesitamos recrear el contexto de la vista ver_carrito)
        items = []
        total = 0
        for id, detalles in carrito.items():
            subtotal = detalles['precio'] * detalles['cantidad']
            total += subtotal
            items.append({
                'id': id, 'nombre': detalles['nombre'], 'precio': detalles['precio'],
                'cantidad': detalles['cantidad'], 'imagen': detalles['imagen'], 'subtotal': subtotal
            })
        return render(request, 'paginasenlace/carrito.html', {'items': items, 'total': total, 'form': form})

    with transaction.atomic():
        total_orden = 0
        for id, detalles in carrito.items():
            producto = get_object_or_404(Producto, id=id)
            if producto.stock < detalles['cantidad']:
                messages.error(request, f'No hay suficiente stock para {producto.nombre}.')
                return redirect('ver_carrito')
            total_orden += detalles['precio'] * detalles['cantidad']

        # Creamos la orden y guardamos los datos del formulario
        orden = form.save(commit=False)
        orden.usuario = request.user
        orden.total = total_orden
        orden.estado = 'Pendiente'
        orden.save()
        
        for id, detalles in carrito.items():
            producto = Producto.objects.get(id=id)
            OrdenProducto.objects.create(
                orden=orden, producto=producto,
                cantidad=detalles['cantidad'], precio=detalles['precio']
            )
            producto.stock -= detalles['cantidad']
            producto.save()

    request.session['carrito'] = {}
    messages.success(request, '¡Tu compra ha sido procesada con éxito!')
    return redirect('farmacia')

# --- VISTA PARA QUE EL ADMIN VEA LAS ÓRDENES ---
@login_required
def admin_ordenes(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    
    ordenes = Orden.objects.all().order_by('-fecha_creacion')
    return render(request, 'paginasenlace/admin_ordenes.html', {'ordenes': ordenes})


@login_required
@require_POST # Para seguridad, solo se puede acceder a través de un formulario POST
def admin_orden_actualizar_estado(request, orden_id, nuevo_estado):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    
    orden = get_object_or_404(Orden, id=orden_id)
    
    # Validamos que el nuevo estado sea uno de los permitidos
    estados_validos = [estado[0] for estado in Orden.ESTADOS]
    if nuevo_estado in estados_validos:
        orden.estado = nuevo_estado
        orden.save()
        messages.success(request, f"La orden #{orden.id} ha sido actualizada a '{nuevo_estado}'.")
    else:
        messages.error(request, "Estado no válido.")

    return redirect('admin_ordenes')

@login_required
@require_POST
def admin_orden_eliminar(request, orden_id):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')

    orden = get_object_or_404(Orden, id=orden_id)
    # Importante: Si se elimina una orden cancelada, el stock NO se devuelve.
    # Si quisieras devolver el stock, se necesitaría una lógica adicional aquí.
    orden.delete()
    messages.success(request, f"La orden #{orden.id} ha sido eliminada.")
    return redirect('admin_ordenes')