
from django import template
from pdb import set_trace

register = template.Library()

@register.filter(name='construct_range') 
def times(number, stop_number):
    if number==stop_number:
        return range(number)
    else:
        return range(number.stop+stop_number, number.stop)