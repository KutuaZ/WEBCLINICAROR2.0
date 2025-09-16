"""
URL configuration for webclinicaROR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from core.views import index_estatico, formulario_reserva, especialidades_estatico, nosotros_estatico, formulario_contacto, formulario_iniciarsesion, farmacia_estatico, formulario_reservalab, formulario_reservaonline, aranceles_estatico, seguros_estatico, formulario_pagocuentas, formulario_soporte, preguntas_estatico

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("index/", index_estatico, name="index"),
    path("reserva/", formulario_reserva, name="reserva"),
    path("especialidades/", especialidades_estatico, name="especialidades"),
    path("nosotros/", nosotros_estatico, name="nosotros"),
    path("contacto/", formulario_contacto, name="contacto"),
    path("iniciarsesion/", formulario_iniciarsesion, name="iniciarsesion"),
    path("farmacia/", farmacia_estatico, name="farmacia"),
    path("reservalab/", formulario_reservalab, name="reservalab"),
    path("reservaonline/", formulario_reservaonline, name="reservaonline"),
    path("aranceles/", aranceles_estatico, name="aranceles"),
    path("seguros", seguros_estatico, name="seguros"),
    path("pagocuentas", formulario_pagocuentas, name="pagocuentas"),
    path("soporte/", formulario_soporte, name="soporte"),
    path("preguntas/", preguntas_estatico, name="preguntas"),
]                           
