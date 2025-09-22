from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from django import forms

# Importaciones correctas y completas de modelos y formularios
from .models import (
    Paciente, Especialidad, Sede, Medico, HoraDisponible, Reserva,
    HistorialMedico, Ticket, Producto, Orden, OrdenProducto, Arancel, Cuenta,
    ResultadoLaboratorio
)
from .forms import (
    ReservaForm, TicketForm, ProductoForm, CheckoutForm, ArancelForm, CuentaForm,
    ReservaLabForm, ReservaOnlineForm
)


# --- Páginas Estáticas / Vistas Públicas ---

def index_estatico(request):
    return render(request, 'paginasinicio/index.html')

def especialidades_estatico(request):
    return render(request, 'paginasinicio/especialidades.html')

def nosotros_estatico(request):
    return render(request, 'paginasinicio/nosotros.html')

def seguros_estatico(request):
    return render(request, 'paginasenlace/seguros.html')

def formulario_soporte(request):
    return render(request, 'paginasenlace/soporte.html')

def preguntas_estatico(request):
    return render(request, 'paginasenlace/preguntas.html')

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
    productos = Producto.objects.all()
    return render(request, 'paginasinicio/farmacia.html', {'productos': productos})

def aranceles_publico(request):
    busqueda = request.GET.get('buscar', '')
    aranceles = Arancel.objects.all()
    if busqueda:
        aranceles = aranceles.filter(
            Q(nombre__icontains=busqueda) |
            Q(codigo__icontains=busqueda)
        )
    return render(request, 'paginasenlace/aranceles.html', {'aranceles': aranceles})

def formulario_pagocuentas(request):
    cuentas = None
    rut_buscado = request.GET.get('rut', '')
    if rut_buscado:
        paciente = Paciente.objects.filter(rut=rut_buscado).first()
        if paciente:
            cuentas = Cuenta.objects.filter(paciente=paciente, pagado=False)
        else:
            messages.info(request, "No se encontró un paciente con el RUT ingresado.")
    return render(request, 'paginasenlace/pagocuentas.html', {'cuentas': cuentas, 'rut_buscado': rut_buscado})


# --- RESERVA ONLINE (TELEMEDICINA) ---
def formulario_reservaonline(request):
    medicos_telemedicina = Medico.objects.filter(tipo='TELEMEDICINA')
    horas_disponibles = HoraDisponible.objects.filter(medico__in=medicos_telemedicina, disponible=True)

    if request.method == 'POST':
        # Usamos el nuevo formulario específico
        form = ReservaOnlineForm(request.POST)
        form.fields['medico'].choices = [(m.id, m.user.get_full_name()) for m in medicos_telemedicina]
        form.fields['hora'].choices = [(h.id, f"{h.hora_inicio}") for h in horas_disponibles]

        if form.is_valid():
            datos = form.cleaned_data
            try:
                hora_obj = HoraDisponible.objects.get(id=datos['hora'], disponible=True)
                medico_obj = Medico.objects.get(id=datos['medico'])
                
                Reserva.objects.create(
                    nombre_paciente=datos['nombre_paciente'], email_paciente=datos['email_paciente'],
                    telefono_paciente=datos['telefono_paciente'], rut_paciente=datos['rut_paciente'],
                    medico=medico_obj, hora_disponible=hora_obj
                )
                
                hora_obj.disponible = False
                hora_obj.save()
                
                messages.success(request, '¡Tu hora de telemedicina ha sido reservada con éxito!')
                return redirect('reservaonline')
            except (HoraDisponible.DoesNotExist, Medico.DoesNotExist):
                messages.error(request, 'La hora o el profesional seleccionados ya no son válidos.')
    else:
        form = ReservaOnlineForm()

    context = {
        'form': form,
        'medicos': medicos_telemedicina,
        'horas': horas_disponibles,
    }
    return render(request, 'paginasenlace/reservaonline.html', context)


# --- RESERVA DE LABORATORIO ---
def formulario_reservalab(request):
    horas_laboratorio = HoraDisponible.objects.filter(medico__tipo='LABORATORIO', disponible=True)

    if request.method == 'POST':
        form = ReservaLabForm(request.POST)
        form.fields['hora'].choices = [(h.id, f"{h.hora_inicio}") for h in horas_laboratorio]

        if form.is_valid():
            datos = form.cleaned_data
            try:
                # --- LÓGICA DE GUARDADO QUE FALTABA ---
                hora_obj = HoraDisponible.objects.get(id=datos['hora'], disponible=True)

                Reserva.objects.create(
                    nombre_paciente=datos['nombre_paciente'], email_paciente=datos['email_paciente'],
                    telefono_paciente=datos['telefono_paciente'], rut_paciente=datos['rut_paciente'],
                    medico=hora_obj.medico,  # El médico se obtiene de la hora seleccionada
                    hora_disponible=hora_obj
                )
                
                # Marcar la hora como no disponible
                hora_obj.disponible = False
                hora_obj.save()
                
                messages.success(request, '¡Tu hora para laboratorio ha sido reservada con éxito!')
                return redirect('reservalab')
            except HoraDisponible.DoesNotExist:
                messages.error(request, 'La hora seleccionada ya no está disponible.')
    else:
        form = ReservaLabForm()

    context = {
        'form': form,
        'horas': horas_laboratorio,
    }
    return render(request, 'paginasenlace/reservalab.html', context)


# --- Autenticación y Registro ---

def iniciar_sesion(request):
    if request.method == "POST":
        email_or_username = request.POST.get("email")
        password = request.POST.get("password")
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
                user = User.objects.create_user(username=email, email=email, password=password)
                user.first_name = nombre
                user.save()
                grupo_paciente, created = Group.objects.get_or_create(name='paciente')
                user.groups.add(grupo_paciente)
                Paciente.objects.create(user=user, telefono=telefono, rut=rut)
            messages.success(request, "¡Registro completado con éxito! Ahora puedes iniciar sesión.")
            return redirect("iniciarsesion")
        except Exception as e:
            messages.error(request, f"Ocurrió un error inesperado: {e}")
            return redirect("registro")
    return render(request, "paginasenlace/registro.html")


# --- Vistas de Reservas y Pacientes/Médicos ---

def vista_reserva(request):
    sedes = Sede.objects.all()
    especialidades = Especialidad.objects.all()
    medicos = Medico.objects.select_related('user', 'especialidad', 'sede').filter(tipo='PRESENCIAL')
    horas = HoraDisponible.objects.filter(disponible=True, medico__tipo='PRESENCIAL').select_related('medico')
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        form.fields['sede'].choices = [(s.id, s.nombre) for s in sedes]
        form.fields['especialidad'].choices = [(e.id, e.nombre) for e in especialidades]
        form.fields['medico'].choices = [(m.id, m.user.get_full_name()) for m in medicos]
        form.fields['hora'].choices = [(h.id, f"{h.hora_inicio.strftime('%H:%M')} - {h.hora_fin.strftime('%H:%M')}") for h in horas]
        if form.is_valid():
            datos = form.cleaned_data
            try:
                hora_obj = HoraDisponible.objects.get(id=datos['hora'], disponible=True)
                medico_obj = Medico.objects.get(id=datos['medico'])
                Reserva.objects.create(
                    nombre_paciente=datos['nombre_paciente'], email_paciente=datos['email_paciente'],
                    telefono_paciente=datos['telefono_paciente'], rut_paciente=datos['rut_paciente'],
                    medico=medico_obj, hora_disponible=hora_obj
                )
                hora_obj.disponible = False
                hora_obj.save()
                messages.success(request, '¡Tu hora ha sido reservada con éxito!')
                return redirect('reserva')
            except (HoraDisponible.DoesNotExist, Medico.DoesNotExist):
                messages.error(request, 'La hora o el médico seleccionados ya no son válidos.')
                return redirect('reserva')
    else:
        form = ReservaForm()
    context = {'form': form, 'sedes': sedes, 'especialidades': especialidades, 'medicos': medicos, 'horas': horas}
    return render(request, 'paginasinicio/reserva.html', context)

@login_required
def agenda_medico(request):
    reservas = []
    try:
        medico = Medico.objects.get(user=request.user)
        reservas = Reserva.objects.filter(medico=medico).select_related('hora_disponible')
    except Medico.DoesNotExist:
        pass
    return render(request, 'paginasenlace/agenda.html', {'reservas': reservas})

@login_required
def historial_paciente_rut(request, rut):
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
                paciente_obj = Paciente.objects.filter(rut=reserva.rut_paciente).first()
                HistorialMedico.objects.create(
                    paciente=paciente_obj, medico=medico_actual,
                    reserva=reserva, descripcion=descripcion
                )
                messages.success(request, "Historial agregado con éxito.")
            else:
                messages.error(request, "No tienes permiso para modificar esta reserva.")
        else:
            messages.error(request, "Faltan datos para agregar el historial.")
        return redirect('historial_paciente_rut', rut=rut)
    reservas = Reserva.objects.filter(rut_paciente=rut).select_related(
        'medico__user', 'medico__especialidad', 'hora_disponible'
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
        paciente = Paciente.objects.get(user=request.user)
        historiales = HistorialMedico.objects.filter(paciente=paciente).order_by('-reserva__hora_disponible__fecha')
        context = {
            'historiales': historiales,
            'nombre_paciente': f"{paciente.user.first_name} {paciente.user.last_name}",
            'rut_paciente': paciente.rut,
        }
        return render(request, 'paginasenlace/historial_personal.html', context)
    except Paciente.DoesNotExist:
        messages.error(request, 'No se encontró un perfil de paciente asociado a su cuenta.')
        return redirect('index')

@login_required
def vista_resultados_laboratorio(request):
    try:
        paciente = Paciente.objects.get(user=request.user)
        resultados = ResultadoLaboratorio.objects.filter(paciente=paciente).order_by('-fecha_subido')
    except Paciente.DoesNotExist:
        messages.error(request, "No se encontró un perfil de paciente asociado a su cuenta.")
        return redirect('index')

    return render(request, 'paginasenlace/resultados_laboratorio.html', {'resultados': resultados})


# --- Vistas de Administración (Admin-Web) ---

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
    if not request.user.groups.filter(name='admin-web').exists(): return redirect('index')
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
    if not request.user.groups.filter(name='admin-web').exists(): return redirect('index')
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
    if not request.user.groups.filter(name='admin-web').exists(): return redirect('index')
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect('admin_farmacia')

@login_required
def admin_pagos(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    
    paciente = None
    cuentas = []
    rut_buscado = request.GET.get('rut', '')
    
    if rut_buscado:
        paciente = Paciente.objects.filter(rut=rut_buscado).first()
        if paciente:
            cuentas = Cuenta.objects.filter(paciente=paciente)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add' and paciente:
            post_data = request.POST.copy()
            post_data['paciente'] = paciente.id
            cuenta_form = CuentaForm(post_data)
            if cuenta_form.is_valid():
                cuenta_form.save()
                messages.success(request, 'Cuenta agregada correctamente.')
                return redirect(f"{request.path_info}?rut={rut_buscado}")
        
        elif action == 'edit':
            cuenta_id = request.POST.get('cuenta_id')
            cuenta = get_object_or_404(Cuenta, id=cuenta_id)
            cuenta.monto = request.POST.get('monto')
            cuenta.pagado = 'pagado' in request.POST
            cuenta.save()
            messages.success(request, 'Cuenta actualizada.')
            return redirect(f"{request.path_info}?rut={rut_buscado}")

        elif action == 'delete':
            cuenta_id = request.POST.get('cuenta_id')
            get_object_or_404(Cuenta, id=cuenta_id).delete()
            messages.success(request, 'Cuenta eliminada.')
            return redirect(f"{request.path_info}?rut={rut_buscado}")

    initial_data = {'paciente': paciente} if paciente else {}
    cuenta_form = CuentaForm(initial=initial_data)
    if paciente:
        cuenta_form.fields['paciente'].widget = forms.HiddenInput()
        
    aranceles_disponibles = Arancel.objects.all()
    
    return render(request, 'paginasenlace/admin_pagos.html', {
        'paciente': paciente, 'cuentas': cuentas,
        'rut_buscado': rut_buscado, 'cuenta_form': cuenta_form,
        'aranceles_disponibles': aranceles_disponibles
    })

@login_required
def admin_aranceles(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    aranceles = Arancel.objects.all()
    form = ArancelForm()
    if request.method == 'POST':
        form = ArancelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Arancel agregado correctamente.')
            return redirect('admin_aranceles')
    return render(request, 'paginasenlace/admin_aranceles.html', {'form': form, 'aranceles': aranceles})

@login_required
def admin_arancel_editar(request, arancel_id):
    if not request.user.groups.filter(name='admin-web').exists(): return redirect('index')
    arancel = get_object_or_404(Arancel, id=arancel_id)
    if request.method == 'POST':
        form = ArancelForm(request.POST, instance=arancel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Arancel actualizado.')
            return redirect('admin_aranceles')
    else:
        form = ArancelForm(instance=arancel)
    return render(request, 'paginasenlace/admin_arancel_form.html', {'form': form})

@login_required
def admin_arancel_eliminar(request, arancel_id):
    if not request.user.groups.filter(name='admin-web').exists(): return redirect('index')
    arancel = get_object_or_404(Arancel, id=arancel_id)
    arancel.delete()
    messages.success(request, 'Arancel eliminado.')
    return redirect('admin_aranceles')

@login_required
def admin_ordenes(request):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    ordenes = Orden.objects.all().order_by('-fecha_creacion')
    return render(request, 'paginasenlace/admin_ordenes.html', {'ordenes': ordenes})

@login_required
@require_POST
def admin_orden_actualizar_estado(request, orden_id, nuevo_estado):
    if not request.user.groups.filter(name='admin-web').exists():
        messages.error(request, "Acceso no autorizado.")
        return redirect('index')
    orden = get_object_or_404(Orden, id=orden_id)
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
    orden.delete()
    messages.success(request, f"La orden #{orden.id} ha sido eliminada.")
    return redirect('admin_ordenes')


# --- Vistas del Carrito de Compras ---

@require_POST
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre, 'precio': int(producto.precio),
            'cantidad': 1, 'imagen': producto.imagen.url if producto.imagen else ''
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
            'id': id, 'nombre': detalles['nombre'], 'precio': detalles['precio'],
            'cantidad': detalles['cantidad'], 'imagen': detalles['imagen'], 'subtotal': subtotal
        })
    form = CheckoutForm()
    return render(request, 'paginasenlace/carrito.html', {'items': items, 'total': total, 'form': form})

@require_POST
def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')

@login_required
@require_POST
def procesar_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('farmacia')
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Por favor, completa correctamente los datos de envío.')
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
        total_orden = sum(d['precio'] * d['cantidad'] for d in carrito.values())
        for id, detalles in carrito.items():
            producto = get_object_or_404(Producto, id=id)
            if producto.stock < detalles['cantidad']:
                messages.error(request, f'No hay suficiente stock para {producto.nombre}.')
                return redirect('ver_carrito')
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