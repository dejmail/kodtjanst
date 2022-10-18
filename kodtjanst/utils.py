from bs4 import BeautifulSoup
from django.utils.html import format_html

def make_string_html_safe(html):
    if bool(BeautifulSoup(html, "html.parser").find()) == True:
        return format_html(html)
    else:
        return html
