from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

# Páginas estáticas
def index_estatico(request):
    return render(request, 'paginasinicio/index.html')

def formulario_reserva(request):
    return render(request, 'paginasinicio/reserva.html')

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

