from django import template
import datetime

#
# Source: https://stackoverflow.com/questions/46349178/how-do-you-format-from-unix-time-stamp-to-local-time-in-django
#

register = template.Library()


@register.filter(name='unix_to_datetime')
def unix_to_datetime(value):
    return datetime.datetime.fromtimestamp(int(value))


@register.filter(name='addstr')
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)


@register.filter(name='as_directory')
def as_directory(directory):
    return '/'.join(directory.split("|")[1:])
