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


@register.filter(name='filename_to_path')
def filename_to_path(filepath):
    return 'home|'+'|'.join(filepath.split("/")[:-1]) if filepath.split("/")[:-1] else 'home'

@register.filter(name='file_in_path')
def file_in_path(filepath):
    return filepath.split("/")[-1]

@register.filter(name='filepath_to_url')
def filepath_to_url(file_path):
    file_path = file_path.replace(" ", "%20").split("/")
    if len(file_path) == 1:
        return f"home/{file_path[0]}"
    else:
        return f"home|{"|".join(file_path[:-1])}/{file_path[-1]}"
