from django.template import Variable, VariableDoesNotExist
from django import template
import re
from pdb import set_trace

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
        Returns the value turned into a list.
    """
    matches = ['länk','klartext']
    if value:
        ret_dict = {}
        if all(x in value for x in matches):
            split_text = re.split(r'\blänk=\b|\bklartext=\b', value)
            ret_dict['länk'] = split_text[1]
            ret_dict['klartext'] = split_text[2]
            return ret_dict
        else:
            return value
    return value    