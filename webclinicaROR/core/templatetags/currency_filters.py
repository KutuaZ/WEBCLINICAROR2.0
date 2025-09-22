from django import template
import locale

register = template.Library()

@register.filter(name='clp_format')
def clp_format(value):
    """
    Formatea un número como moneda chilena (ej: 19990 -> $19.990).
    """
    try:
        locale.setlocale(locale.LC_ALL, 'es_CL.UTF-8')
        return locale.currency(value, grouping=True, symbol='$', international=False)
    except locale.Error:
        
        try:
            val = int(value)
            
            return f"${val:,.0f}".replace(',', '.')
        except (ValueError, TypeError):
            return value