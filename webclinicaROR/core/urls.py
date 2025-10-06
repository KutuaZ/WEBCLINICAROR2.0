from django.urls import path
from . import views

    
    
app_name = 'core'
    
    
    
    
urlpatterns = [
    # API 
    path("api/especialidades/", views.listar_especialidades, name="listar_especialidades"),
    path("api/sedes/", views.listar_sedes, name="listar_sedes"),
    path("api/medicos/", views.listar_medicos, name="listar_medicos"),
    path("api/horas_disponibles/", views.listar_horas_disponibles, name="listar_horas_disponibles"),
    path("api/reservas/", views.listar_reservas, name="listar_reservas"),
    path("api/pacientes/", views.listar_pacientes, name="listar_pacientes"),
    path("api/historiales_medicos/", views.listar_historiales_medicos, name="listar_historiales_medicos"),
    path("api/tickets/", views.listar_tickets, name="listar_tickets"),
    path("api/productos/", views.listar_productos, name="listar_productos"),
    path("api/ordenes/", views.listar_ordenes, name="listar_ordenes"),
    path("api/ordenes_productos/", views.listar_orden_productos, name="listar_ordenes_productos"),
    path("api/aranceles/", views.listar_aranceles, name="listar_aranceles"),
    path("api/cuentas/", views.listar_cuentas, name="listar_cuentas"),
    path("api/resultados_laboratorio/", views.listar_resultados_laboratorio, name="listar_resultados_laboratorio"),
    path("api/auth/login/", views.login_api, name="login_api"),
    path("api/auth/perfil/", views.perfil_usuario, name="perfil_usuario"),


    path("api/indicadores-economicos/", views.indicadores_economicos_api, name="indicadores_economicos_api"),
    path("api/clima-salud/", views.clima_salud_api, name="clima_salud_api"),  

]

    