import os

from django import template
from django.utils.safestring import mark_safe

from main.const import IMG_EXT_WITH_DOT, IMAGE_SIZES_INDEX, SLIDER_TYPE_SWBH, MAX_SIZE_PRO_IMAGES
from main.models import ProductAttribute, Product, OrderPayment, ProductAttributeCombination, ProductAttributeGroup, \
    Category, Post
from spa import settings

register = template.Library()


@register.filter(name='cut')
def cut(value, arg):
    return value.replace(arg, '')


@register.simple_tag
def thumbnail(obj, typ='sm', *args, **kwargs):
    if typ is None or typ not in ['sm', 'mid', 'big', 'hsm', 'hmid', 'hbig']:
        typ = 'sm'
    (x, y) = IMAGE_SIZES_INDEX[typ]
    found = False
    thumb = ""
    if obj is not None and isinstance(obj, Post):
        real = settings.MEDIA_ROOT + '/{}/{}/'.format(obj.CONST_TYPE, str(obj.pk))
        path = settings.MEDIA_URL + '{}/{}/'.format(obj.CONST_TYPE, str(obj.pk))
        for i in range(1, MAX_SIZE_PRO_IMAGES):
            name = "{}_{}x{}.jpg".format(i, x, y)
            exist = real + name
            if os.path.exists(exist):
                thumb = name
                found = True
                break
    if not found:
        _name = "{}_{}x{}".format(str(obj.pk), x, y)
        real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/'
        path = settings.MEDIA_URL + obj.CONST_TYPE + '/'
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
        thumb = settings.MEDIA_URL + "noimage_{}x{}.jpg".format(x, y)
    return thumb


@register.simple_tag
def thumbnail_alt(obj, typ='sm', *args, **kwargs):
    if typ is None or typ not in ['sm', 'mid', 'big', 'hsm', 'hmid', 'hbig']:
        typ = 'sm'
    (x, y) = IMAGE_SIZES_INDEX[typ]
    real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/' + str(obj.pk) + '/'
    path = settings.MEDIA_URL + obj.CONST_TYPE + '/' + str(obj.pk) + '/'
    found = False
    thumb = ""
    for i in range(1, 10):
        _name = "{}_{}x{}".format(str(i), x, y)
        for ext in IMG_EXT_WITH_DOT:
            name = _name + ext
            exist = real + name
            if os.path.exists(exist):
                thumb = name
                found = True
                break
        if found:
            break
    if found:
        thumb = path + thumb
    else:
        thumb = settings.MEDIA_URL + "noimage.jpg"
    return thumb


@register.filter
def modulo(num, val):
    return num % val


@register.simple_tag
def get_list_pro(obj, *args, **kwargs):
    if not isinstance(obj, Category):
        return None
    products = obj.products.all()
    return products


@register.simple_tag
def get_list_pro_att(obj, *args, **kwargs):
    if not isinstance(obj, Product):
        return None
    pro_atts = ProductAttribute.objects.filter(product_id=obj.product_id)
    return pro_atts


# using render in django
@register.inclusion_tag('shop/slider_product.html')
def load_slider(model=None, *args, **kwargs):
    images = {}
    if model is not None and isinstance(model, int):
        try:
            model = ProductAttribute.objects.get(pk=model)
        except OrderPayment.DoesNotExist:
            return {'images': images, 'model': model}
    if model is None or not isinstance(model, ProductAttribute) or not isinstance(model.CONST_TYPE,
                                                                                  str) or not isinstance(model.pk, int):
        return {'images': images, 'model': model}
    else:
        folder = "{}/{}".format(model.CONST_TYPE, model.pk)
        path = settings.MEDIA_ROOT + '/' + folder
        path_url = settings.MEDIA_URL + folder
        (x, y) = SLIDER_TYPE_SWBH['thumbnail']
        (bx, by) = SLIDER_TYPE_SWBH['big']
        for i in range(1, SLIDER_TYPE_SWBH['sizes'] + 1):
            name = "{}_{}x{}.jpg".format(i, x, y)
            sm = path + '/' + name
            bname = "{}_{}x{}.jpg".format(i, bx, by)
            big = path + '/' + bname
            if os.path.exists(sm) and os.path.exists(big):
                sm_url = path_url + '/' + name
                big_url = path_url + '/' + bname
            else:
                name = "{}_{}x{}.jpg".format('noimage', x, y)
                bname = "{}_{}x{}.jpg".format('noimage', bx, by)
                sm_url = settings.MEDIA_URL + name
                big_url = settings.MEDIA_URL + bname
            images[mark_safe(sm_url)] = mark_safe(big_url)
    return {'images': images, 'model': model}


@register.inclusion_tag('shop/variant_product.html')
def load_variant(model=None, *args, **kwargs):
    variants = {}
    if model is not None and isinstance(model, int):
        try:
            model = ProductAttribute.objects.get(pk=model)
        except OrderPayment.DoesNotExist:
            return {'variants': variants, 'model': model}

    if model is None or not isinstance(model, ProductAttribute) or not isinstance(model.CONST_TYPE,
                                                                                  str) or not isinstance(model.pk, int):
        return {'variants': variants, 'model': model}
    combines = ProductAttributeCombination.objects.filter(pro_attribute_id=model).order_by(
        '-attribute_id__attr_group_id')
    act_value = []
    for combine in combines:
        act_value.append(combine.attribute_id.pk)
        # replace by subquery in django???
        attributes = ProductAttributeGroup.objects.filter(attr_group_id=combine.attribute_id.attr_group_id,
                                                          product_id=model.product_id).order_by('-attr_group_id')
        objs = []
        for obj in attributes:
            objs.append(obj.attribute_id)
        variants[combine.attribute_id.attr_group_id.name] = objs
    return {'variants': variants, 'model': model, 'act_value': act_value}


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def count_items_in_product(product):
    count = 0
    if product is not None and isinstance(product, int):
        try:
            product = Product.objects.get(pk=product)
        except Product.DoesNotExist:
            product = None
    if product is not None and isinstance(product, Product):
        count = ProductAttribute.objects.filter(product_id=product).count()
    return count
