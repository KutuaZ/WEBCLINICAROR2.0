from django import template
import locale

register = template.Library()

@register.filter(name='clp_format')
def clp_format(value):
    """
    Formatea un número como moneda chilena (ej: 19990 -> $19.990).
    """
    try:
        # Intentamos configurar la localización para Chile. Puede fallar en algunos sistemas.
        locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
        return locale.currency(value, grouping=True, symbol='$', international=False)
    except locale.Error:
        # Si falla, usamos un formateo manual que siempre funciona.
        try:
            val = int(value)
            # Formatea con comas y luego reemplaza por puntos.
            return f"${val:,.0f}".replace(',', '.')
        except (ValueError, TypeError):
            return value