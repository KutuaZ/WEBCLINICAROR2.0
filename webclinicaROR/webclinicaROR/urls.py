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
from django.urls import path, include
from core import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    
    # Páginas estáticas
    path('', views.index_estatico, name='home'),
    path('index/', views.index_estatico, name='index'),
    path('especialidades/', views.especialidades_estatico, name='especialidades'),
    path('nosotros/', views.nosotros_estatico, name='nosotros'),
    path('contacto/', views.formulario_contacto, name='contacto'),
    path('farmacia/', views.farmacia_estatico, name='farmacia'),
    path('reservalab/', views.formulario_reservalab, name='reservalab'),
    path('reservaonline/', views.formulario_reservaonline, name='reservaonline'),
    path('aranceles/', views.aranceles_estatico, name='aranceles'),
    path('seguros/', views.seguros_estatico, name='seguros'),
    path('pagocuentas/', views.formulario_pagocuentas, name='pagocuentas'),
    path('soporte/', views.formulario_soporte, name='soporte'),
    path('preguntas/', views.preguntas_estatico, name='preguntas'),
    path('agenda/', views.agenda_estatico, name='agenda'),
    path('reserva/', views.vista_reserva, name='reserva'),
    path('Historial/<int:paciente_id>/', views.historial_paciente, name='historial_paciente'),
    path('agregar_historial/<int:reserva_id>/', views.agregar_historial, name='agregar_historial'),
    path('HistorialRut/<str:rut>/', views.historial_paciente_rut, name='historial_paciente_rut'),
    path('historial_personal/', views.historial_personal, name='historial_personal'),
    
    # --- NUEVAS URLS PARA LA FARMACIA ---
    path('admin-portal/farmacia/', views.admin_farmacia, name='admin_farmacia'),
    path('admin-portal/farmacia/crear/', views.admin_producto_crear, name='admin_producto_crear'),
    path('admin-portal/farmacia/editar/<int:producto_id>/', views.admin_producto_editar, name='admin_producto_editar'),
    path('admin-portal/farmacia/eliminar/<int:producto_id>/', views.admin_producto_eliminar, name='admin_producto_eliminar'),
    
    path('admin-portal/pagos/', views.admin_pagos, name='admin_pagos'),
    path('admin-portal/aranceles/', views.admin_aranceles, name='admin_aranceles'),
    



    # Usuarios: login, logout, registro
    path('iniciarsesion/', views.iniciar_sesion, name='iniciarsesion'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('registro/', views.registro, name='registro'),

    # Reset de contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
