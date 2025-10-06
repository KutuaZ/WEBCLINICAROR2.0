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
        
        

@register.filter
def div(value, divisor):
    """Divide dos números para conversiones de moneda"""
    try:
        return float(value) / float(divisor)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def to_usd(value, dolar_rate):
    """Convierte pesos chilenos a dólares"""
    try:
        usd_value = float(value) / float(dolar_rate)
        return f"${usd_value:.2f}"
    except (ValueError, ZeroDivisionError):
        return "$0.00"

@register.filter  
def to_eur(value, euro_rate):
    """Convierte pesos chilenos a euros"""
    try:
        eur_value = float(value) / float(euro_rate)
        return f"€{eur_value:.2f}"
    except (ValueError, ZeroDivisionError):
        return "€0.00"