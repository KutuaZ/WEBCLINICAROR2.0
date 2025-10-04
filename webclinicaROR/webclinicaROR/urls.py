
from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Páginas estáticas y principales
    path('', views.index_estatico, name='home'),
    path('index/', views.index_estatico, name='index'),
    path('especialidades/', views.especialidades_estatico, name='especialidades'),
    path('nosotros/', views.nosotros_estatico, name='nosotros'),
    path('contacto/', views.formulario_contacto, name='contacto'),
    path('farmacia/', views.farmacia_estatico, name='farmacia'),
    path('reservalab/', views.formulario_reservalab, name='reservalab'),
    path('reservaonline/', views.formulario_reservaonline, name='reservaonline'),
    path('aranceles/', views.aranceles_publico, name='aranceles'),
    path('seguros/', views.seguros_estatico, name='seguros'),
    path('pagocuentas/', views.formulario_pagocuentas, name='pagocuentas'),
    path('soporte/', views.formulario_soporte, name='soporte'),
    path('preguntas/', views.preguntas_estatico, name='preguntas'),
    path('reserva/', views.vista_reserva, name='reserva'),

    # Vistas de Usuarios Logueados
    path('agenda/', views.agenda_medico, name='agenda'), # Se cambió 'agenda_estatico' por 'agenda_medico'
    path('historial/<str:rut>/', views.historial_paciente_rut, name='historial_paciente_rut'),
    path('historial_personal/', views.historial_personal, name='historial_personal'),
    path('resultados-laboratorio/', views.vista_resultados_laboratorio, name='resultados_laboratorio'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    
    # Administración (Admin-Web)
    path('admin-portal/farmacia/', views.admin_farmacia, name='admin_farmacia'),
    path('admin-portal/farmacia/crear/', views.admin_producto_crear, name='admin_producto_crear'),
    path('admin-portal/farmacia/editar/<int:producto_id>/', views.admin_producto_editar, name='admin_producto_editar'),
    path('admin-portal/farmacia/eliminar/<int:producto_id>/', views.admin_producto_eliminar, name='admin_producto_eliminar'),
    path('admin-portal/pagos/', views.admin_pagos, name='admin_pagos'),
    path('admin-portal/aranceles/', views.admin_aranceles, name='admin_aranceles'),
    path('admin-portal/aranceles/editar/<int:arancel_id>/', views.admin_arancel_editar, name='admin_arancel_editar'),
    path('admin-portal/aranceles/eliminar/<int:arancel_id>/', views.admin_arancel_eliminar, name='admin_arancel_eliminar'),
    path('admin-portal/ordenes/', views.admin_ordenes, name='admin_ordenes'),
    path('admin-portal/ordenes/actualizar/<int:orden_id>/<str:nuevo_estado>/', views.admin_orden_actualizar_estado, name='admin_orden_actualizar_estado'),
    path('admin-portal/ordenes/eliminar/<int:orden_id>/', views.admin_orden_eliminar, name='admin_orden_eliminar'),

    # Carrito de Compras
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('compra/procesar/', views.procesar_compra, name='procesar_compra'),

    # Autenticación
    path('iniciarsesion/', views.iniciar_sesion, name='iniciarsesion'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('registro/', views.registro, name='registro'),

    # Reset de Contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='paginasenlace/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='paginasenlace/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='paginasenlace/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='paginasenlace/password_reset_complete.html'), name='password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)