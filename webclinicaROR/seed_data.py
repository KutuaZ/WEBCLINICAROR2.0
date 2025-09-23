import os
import django
from datetime import date, time, timedelta

# Configura el entorno de Django para poder usar los modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webclinicaROR.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import (
    Especialidad, Sede, Medico, Paciente, HoraDisponible, Arancel, 
    Producto, Cuenta, Ticket
)

def run():
    print("--- Limpiando datos antiguos de la base de datos...")
    # Limpiar en orden inverso para evitar problemas de dependencias
    Cuenta.objects.all().delete()
    Arancel.objects.all().delete()
    Producto.objects.all().delete()
    HoraDisponible.objects.all().delete()
    Paciente.objects.all().delete()
    Medico.objects.all().delete()
    Especialidad.objects.all().delete()
    Sede.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()
    Group.objects.all().delete()
    # Eliminar al superusuario si existe para asegurar un estado limpio
    User.objects.filter(is_superuser=True).delete()
    print("Limpieza completada.")

    print("\n--- Iniciando la carga de datos de prueba ---")

    # 1. Creación de Grupos
    print("Creando grupos de usuarios (paciente, med, admin-web)...")
    grupo_paciente, _ = Group.objects.get_or_create(name='paciente')
    grupo_medico, _ = Group.objects.get_or_create(name='med')
    grupo_admin_web, _ = Group.objects.get_or_create(name='admin-web')

    # 2. Creación de Sedes y Especialidades
    print("Creando sedes y especialidades...")
    sedes = {
        'stgo': Sede.objects.create(nombre='Santiago'),
        'antof': Sede.objects.create(nombre='Antofagasta'),
        'vina': Sede.objects.create(nombre='Viña del Mar'),
        'pv': Sede.objects.create(nombre='Puerto Varas'),
    }
    especialidades = {
        'general': Especialidad.objects.create(nombre='Medicina General'),
        'cardio': Especialidad.objects.create(nombre='Cardiología'),
        'pedia': Especialidad.objects.create(nombre='Pediatría'),
        'derma': Especialidad.objects.create(nombre='Dermatología'),
        'gine': Especialidad.objects.create(nombre='Ginecología'),
        'neuro': Especialidad.objects.create(nombre='Neurología'),
    }

    # 3. Creación de Usuarios y Perfiles
    print("Creando perfiles de usuario (Admins, Médicos, Pacientes)...")
    
    # Perfil: Superusuario (solo para /admin/ y control total)
    User.objects.create_superuser('admin@ror.cl', 'admin@ror.cl', 'admin1234')

    # Perfil: Administrador Web (para gestionar el sitio y ver tickets)
    admin_web_user = User.objects.create_user('admin.web@ror.cl', 'admin.web@ror.cl', 'adminweb1234')
    admin_web_user.first_name = "Admin"
    admin_web_user.last_name = "Web"
    admin_web_user.is_staff = True  # <-- PERMISO PARA ENTRAR AL DJANGO ADMIN
    admin_web_user.groups.add(grupo_admin_web)
    
    # Asignar permisos para el modelo Ticket
    content_type = ContentType.objects.get_for_model(Ticket)
    ticket_permissions = Permission.objects.filter(content_type=content_type)
    admin_web_user.user_permissions.set(ticket_permissions)
    admin_web_user.save()


    # Perfiles de Médicos
    medicos_data = [
        {'user': ('medico.perez@ror.cl', 'Carlos', 'Pérez'), 'especialidad': especialidades['cardio'], 'sede': sedes['stgo'], 'tipo': 'PRESENCIAL'},
        {'user': ('medico.gomez@ror.cl', 'Ana', 'Gómez'), 'especialidad': especialidades['pedia'], 'sede': sedes['antof'], 'tipo': 'PRESENCIAL'},
        {'user': ('medico.lopez@ror.cl', 'Maria', 'López'), 'especialidad': especialidades['derma'], 'sede': sedes['vina'], 'tipo': 'PRESENCIAL'},
        {'user': ('medico.diaz@ror.cl', 'Javier', 'Díaz'), 'especialidad': especialidades['gine'], 'sede': sedes['pv'], 'tipo': 'PRESENCIAL'},
        {'user': ('medico.online@ror.cl', 'Sofia', 'Rojas'), 'especialidad': especialidades['general'], 'tipo': 'TELEMEDICINA'},
        {'user': ('laboratorio.stgo@ror.cl', 'Lab', 'Santiago'), 'tipo': 'LABORATORIO', 'sede': sedes['stgo']},
    ]
    
    medicos_creados = []
    for data in medicos_data:
        user_info = data['user']
        user = User.objects.create_user(user_info[0], user_info[0], 'medico1234')
        user.first_name, user.last_name = user_info[1], user_info[2]
        user.groups.add(grupo_medico)
        user.save()
        
        medico_args = {'user': user, 'tipo': data['tipo']}
        if 'especialidad' in data:
            medico_args['especialidad'] = data['especialidad']
        if 'sede' in data:
            medico_args['sede'] = data['sede']
        
        medico = Medico.objects.create(**medico_args)
        medicos_creados.append(medico)

    # Perfiles de Pacientes
    pacientes_data = [
        {'user': ('paciente.soto@email.com', 'Juan', 'Soto'), 'rut': '11.111.111-1', 'telefono': '+56911111111'},
        {'user': ('paciente.gonzalez@email.com', 'Maria', 'González'), 'rut': '22.222.222-2', 'telefono': '+56922222222'},
    ]
    
    pacientes_creados = []
    for data in pacientes_data:
        user_info = data['user']
        user = User.objects.create_user(user_info[0], user_info[0], 'paciente1234')
        user.first_name, user.last_name = user_info[1], user_info[2]
        user.groups.add(grupo_paciente)
        user.save()
        paciente = Paciente.objects.create(user=user, rut=data['rut'], telefono=data['telefono'])
        pacientes_creados.append(paciente)


    # 4. Creación de Horas Disponibles (desde hoy)
    print("Creando horarios para la próxima semana...")
    today = date.today()
    for medico in medicos_creados:
        for i in range(7): # Para los próximos 7 días
            current_date = today + timedelta(days=i)
            if medico.tipo == 'PRESENCIAL':
                for h in [9, 10, 11, 12, 14, 15]: # Horas presenciales
                    HoraDisponible.objects.create(medico=medico, fecha=current_date, hora_inicio=time(h, 0), hora_fin=time(h, 45))
            elif medico.tipo == 'TELEMEDICINA':
                for h in [18, 19, 20]: # Horas de telemedicina
                    HoraDisponible.objects.create(medico=medico, fecha=current_date, hora_inicio=time(h, 0), hora_fin=time(h, 30))
            elif medico.tipo == 'LABORATORIO':
                for h, m in [(8, 0), (8, 20), (8, 40), (9, 0), (9, 20)]: # Horas de laboratorio
                    HoraDisponible.objects.create(medico=medico, fecha=current_date, hora_inicio=time(h, m), hora_fin=time(h, m+15))


    # 5. Creación de Aranceles
    print("Creando aranceles de ejemplo...")
    Arancel.objects.create(codigo='CONS-GEN', nombre='Consulta Medicina General', precio=35000)
    Arancel.objects.create(codigo='CONS-CARD', nombre='Consulta Cardiología', precio=45000)
    Arancel.objects.create(codigo='CONS-PED', nombre='Consulta Pediatría', precio=40000)
    Arancel.objects.create(codigo='LAB-SANG', nombre='Examen de Sangre Completo', precio=25000)
    Arancel.objects.create(codigo='LAB-URI', nombre='Examen de Orina', precio=15000)

    # 6. Creación de Productos de Farmacia
    print("Omitiendo creación de productos. Deben ser creados desde la cuenta de admin-web.")

    # 7. Creación de Cuentas Pendientes
    print("Creando cuentas pendientes para pacientes de prueba...")
    Cuenta.objects.create(paciente=pacientes_creados[0], concepto='Consulta Dermatología (anterior)', monto=40000, pagado=False)
    Cuenta.objects.create(paciente=pacientes_creados[1], concepto='Examen de Laboratorio', monto=15000, pagado=False)


    print("\n¡Carga de datos completada exitosamente!")
    print("--------------------------------------------------")
    print("CUENTAS DE PRUEBA CREADAS:")
    print("--------------------------------------------------")
    print("1. Superusuario (Control total del sistema desde /admin/):")
    print("   - Usuario: admin@ror.cl")
    print("   - Clave:   admin1234\n")
    print("2. Administrador Web (Gestión del sitio y Tickets desde /admin/):")
    print("   - Usuario: admin.web@ror.cl")
    print("   - Clave:   adminweb1234\n")
    print("3. Médicos Presenciales (Clave para todos: medico1234):")
    print("   - Usuario: medico.perez@ror.cl (Cardiología - Santiago)")
    print("   - Usuario: medico.gomez@ror.cl (Pediatría - Antofagasta)")
    print("   - Usuario: medico.lopez@ror.cl (Dermatología - Viña del Mar)")
    print("   - Usuario: medico.diaz@ror.cl (Ginecología - Puerto Varas)")
    print("\n4. Médico Telemedicina (Clave: medico1234):")
    print("   - Usuario: medico.online@ror.cl (Medicina General)")
    print("\n5. Personal de Laboratorio (Clave: medico1234):")
    print("   - Usuario: laboratorio.stgo@ror.cl (Santiago)")
    print("\n6. Pacientes (Clave para todos: paciente1234):")
    print("   - Usuario: paciente.soto@email.com")
    print("   - Usuario: paciente.gonzalez@email.com")
    print("--------------------------------------------------")


# Ejecutar la función principal
if __name__ == '__main__':
    run()