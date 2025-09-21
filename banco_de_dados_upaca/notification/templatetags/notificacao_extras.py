from django import template

register = template.Library()

@register.filter
def get_dict_value(d, key):
    return d.get(key, 0)  # retorna 0 se a chave não existir
