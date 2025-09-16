from django.shortcuts import render

# Create your views here.
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

def formulario_iniciarsesion(request):
    return render(request, 'paginasinicio/iniciarsesion.html')

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