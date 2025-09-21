# em seu templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def tipo_display(value):
    mapping = {
        "alvara": "Alvarás",
        "transferencia": "Transferências",
        "revogacao": "Revogações",
        "pdi": "PDI's",
    }
    return mapping.get(value, value.capitalize())
