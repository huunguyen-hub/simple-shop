import datetime
import pdb
from decimal import Decimal

from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.backends.db import SessionStore
from django.core import serializers
from django.http import HttpResponseRedirect
from tox.package import view

from main.models import Cart, CartItem, ProductAttribute, OrderItem
from spa import settings
from spa.secrets import password_encrypt, password_decrypt
from spa.settings import SECRET_KEY
from spa.utils import to_python, preview


def attach_cart(sender, **kwargs):
    user = kwargs.get('user')
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    request = kwargs.get('request')
    session = kwargs.get('request').session
    cart = session.get(settings.CART_SESSION_ID)
    current_user = request.user
    try:
        cart_obj = Cart.objects.get(owner=current_user)
    except Cart.DoesNotExist:
        cart_obj = Cart.objects.create(owner=current_user, status=1)
    if not cart:
        # save an empty cart in the session
        cart = session[settings.CART_SESSION_ID] = {}
    else:
        # load items from session and add to database
        for key, value in cart.items():
            try:
                obj_item = CartItem.objects.get(cart_id=cart_obj, find_item_id=key)
            except CartItem.DoesNotExist:
                obj_item = CartItem.objects.create(cart_id=cart_obj, find_item_id=key)
            if to_python(value['obj']):
                _item = next(serializers.deserialize("json", value['obj'])).object if 'obj' in value else None
            else:
                _item = None
            if _item is not None and isinstance(_item, ProductAttribute):
                obj_item.find_item_id = key
                obj_item.class_of_item = value['obj']
                obj_item.name = value['name']
                obj_item.price = _item.price
                obj_item.original_price = obj_item.price
                obj_item.quantity = value['quantity']
                obj_item.total_price = Decimal(obj_item.price) * value['quantity']
                obj_item.save()
    # load items from database and add to session
    items = CartItem.objects.filter(cart_id=cart_obj)
    for item in items:
        if to_python(item.class_of_item):
            _item = next(serializers.deserialize("json", item.class_of_item)).object
        else:
            item.delete()
            continue  # _item can not convert json we will delete error record in database
        if isinstance(_item, ProductAttribute):
            cart[item.find_item_id] = {
                'userid': request.user.id,
                'item_id': _item.pk,
                'obj': item.class_of_item,
                'name': item.name,
                'quantity': int(item.quantity),
                'price': str(_item.price),
                'image': preview(_item, 'mid')
            }
    session[settings.CART_SESSION_ID] = cart
    session.modified = True


user_logged_in.connect(attach_cart)


def cal_best_items():
    _items = [
        (next(serializers.deserialize("json", item.class_of_item)).object if to_python(item.class_of_item) else None)
        for item in OrderItem.objects.all().order_by('order_id', '-find_item_id')[:5]]
    items = []
    for item in _items:
        if item is not None and isinstance(item, ProductAttribute):
            items.append(item)
    return items


def get_wish_list(request):
    # session = request.session
    items = []
    # if request.user.is_authenticated:
    #     print(request.user)
    return items


def get_onclick_items(request):
    items = []
    # if request.user.is_authenticated:
    #     print(request.user.id)
    return items


def basic_context_processor(request):
    s = SessionStore()
    s['dev_by'] = 'Huu Nguyen'
    s.save()
    current_datetime = datetime.datetime.now()
    new_context = {
        'has_sidebar_right': False,
        'has_sidebar_left': False
    }
    current_context = {
        'app': request.resolver_match.app_name,
        'controller': view.__class__.__module__.split('.')[-1],
        'action': view.__class__.__name__.lower(),
        'best_items': cal_best_items(),
        'wish_items': get_wish_list(request),
        'viewed_items': get_onclick_items(request),
        'current_year': current_datetime.year
    }
    context = {**new_context, **current_context}
    return context


def setCookie(request, response):
    if request.user.is_authenticated() and not request.COOKIES.get('identity'):
        secret = 'username'
        en = password_encrypt(secret.encode(), SECRET_KEY)
        response.set_cookie("identity", en)
    elif not request.user.is_authenticated() and request.COOKIES.get('identity'):
        # else if if no user and cookie remove user cookie, logout
        response.delete_cookie("identity")
    else:
        # update info
        if request.user.is_authenticated() and request.COOKIES.get('identity'):
            current_user = request.user
            print(current_user, request.COOKIES.get('identity'))
    return response


def getCookie(request):
    if not request.user.is_authenticated() and request.COOKIES.get('identity'):
        secret = password_decrypt(request.COOKIES.get('identity'), SECRET_KEY).decode()
        print(secret)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def process_request(request, response):
    # Let's assume that the visitor uses an iPhone...
    request.user_agent.is_mobile  # returns True
    request.user_agent.is_tablet  # returns False
    request.user_agent.is_touch_capable  # returns True
    request.user_agent.is_pc  # returns False
    request.user_agent.is_bot  # returns False

    # Accessing user agent's browser attributes
    request.user_agent.browser  # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
    request.user_agent.browser.family  # returns 'Mobile Safari'
    request.user_agent.browser.version  # returns (5, 1)
    request.user_agent.browser.version_string  # returns '5.1'

    # Operating System properties
    request.user_agent.os  # returns OperatingSystem(family=u'iOS', version=(5, 1), version_string='5.1')
    request.user_agent.os.family  # returns 'iOS'
    request.user_agent.os.version  # returns (5, 1)
    request.user_agent.os.version_string  # returns '5.1'

    # Device properties
    request.user_agent.device  # returns Device(family='iPhone')
    request.user_agent.device.family  # returns 'iPhone'


class LayoutMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response
        self.layout = {
            "en": {"dev_by": "Huu Nguyen"},
            "vn": {"dev_by": "Huu Nguyen"},
        }

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        response.context_data["layout"] = self.layout
        return response
