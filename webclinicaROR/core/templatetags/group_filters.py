from django import template

register = template.Library()

@register.filter(name='es_paciente')
def es_paciente(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='paciente').exists()

@register.filter(name='es_medico')
def es_medico(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='med').exists()

@register.filter
def es_adminweb(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name='admin-web').exists()

