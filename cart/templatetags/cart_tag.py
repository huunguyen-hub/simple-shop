import os
from django.apps import apps
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, Template
from django.utils.safestring import mark_safe
from django.urls import reverse
from main.const import IMAGE_SIZES_INDEX, IMG_EXT_WITH_DOT
from spa import settings

register = template.Library()


# using render in django
@register.simple_tag
def show_payment(order=None, obj=None):
    if order is None or obj is None or not isinstance(obj.CONST_TYPE, str) or not isinstance(obj.pk, int):
        return "Nothing to showing"
    folder = "{}/{}".format(obj.CONST_TYPE, obj.pk)
    path = settings.MEDIA_ROOT + '/' + folder
    result = ''
    for r, d, f in os.walk(path):
        for _file in f:
            # _ext = _file.split(".")[-1].lower()
            (_name, _ext) = _file.split(".")
            if _ext == 'pdf':
                resolved_url = reverse('cart:load_pdf', args=(obj.pk, _name))
                result += '<div class="col-3"><a href="{}"><i class="fa fa-file-pdf-o fa-6" aria-hidden="true">Pdf File</i></a></div>'.format(resolved_url)
            elif ".{}".format(_ext) in IMG_EXT_WITH_DOT:
                resolved_url = reverse('main:shop')
                result += '<div class="col-3"><a href="{}"><i class="fa fa-photo fa-6" aria-hidden="true">Image File</i></a></div>'.format(resolved_url)
            else:
                resolved_url = reverse('cart:load_txt', args=(obj.pk, _name))
                result += '<div class="col-3"><a href="{}"><i class="fa fa-eye"></i>Text File</a></div>'.format(resolved_url)
    return mark_safe(result)


@register.filter()
def item_str(value):
    lst = value.split('_')
    return lst[len(lst)-1]


@register.filter()
def cart_item_str(value):
    lst = value.split('_')
    return "{}_{}".format(lst[len(lst)-2], lst[len(lst)-1])


@register.filter()
def multiply(value, arg):
    return float(value) * arg


# using {{ title|do_something:content }}
@register.filter
def do_something(title, content):
    something = '<h1>%s</h1><p>%s</p>' % (title, content)
    return mark_safe(something)


# using render in django
@register.simple_tag
def headshot(id_obj, name_obj, typ):
    if typ is None or typ not in ['sm', 'mid', 'big', 'hsm', 'hmid', 'hbig']:
        typ = 'sm'
    (x, y) = IMAGE_SIZES_INDEX[typ]
    thumb = ""
    try:
        classified = apps.get_model('main', name_obj)
        obj = classified.objects.get(pk=id_obj)
        _name = "{}_{}x{}".format(str(obj.pk), x, y)
        real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/'
        path = settings.MEDIA_URL + obj.CONST_TYPE + '/'
        found = False
        for ext in IMG_EXT_WITH_DOT:
            name = _name + ext
            exist = real + name
            if os.path.exists(exist):
                thumb = name
                found = True
                break
        if found:
            thumb = path + thumb
        else:
            thumb = settings.MEDIA_URL + "noimage.jpg"
    except (ObjectDoesNotExist, IndexError, ValueError, EnvironmentError):
        thumb = settings.MEDIA_URL + "noimage.jpg"
    return thumb


# using render in django
@register.filter
def do_render(title, content):
    t = Template('This is your <span>{{ message }}</span>.')
    c = Context({'message': '<h1>%s</h1><p>%s</p>' % (title, content)})
    html = t.render(c)
    return mark_safe(html)
