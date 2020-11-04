from decimal import Decimal

from django.conf import settings
from django.core import serializers
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from main.models import CartItem, ProductAttribute, Cart, Address
from spa.utils import preview, to_python


class ItemAlreadyExists(Exception):
    pass


class ItemDoesNotExist(Exception):
    pass


class MyCart(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        if request.user.is_authenticated:
            current_user = request.user
            try:
                cart_obj = Cart.objects.get(owner=current_user)
            except Cart.DoesNotExist:
                cart_obj = Cart.objects.create(owner=current_user, status=1)
            self.cart_obj = cart_obj

    def add_address(self, address):
        if isinstance(address, Address) and isinstance(self.cart_obj, Cart):
            try:
                if self.cart_obj.address is not None and (self.cart_obj.address.pk != address.pk):
                    self.cart_obj.address.delete()  # delete old address
                self.cart_obj.address = address  # add new address
                self.cart_obj.save()
            except ProtectedError:
                address.delete()

    def add(self, item, quantity=1, action=None):
        """
        Add a item to the cart or update its quantity.
        """
        # https://stackoverflow.com/questions/757022/how-do-you-serialize-a-model-instance-in-django
        s_item = serializers.serialize("json", [item])  # convert object to json format
        find_item_id = "{}_{}".format(self.cart_obj.pk, item.pk)
        newItem = True
        if str(find_item_id) not in self.cart.keys():
            self.cart[find_item_id] = {
                'userid': self.request.user.id,
                'item_id': item.pk,
                'obj': s_item,
                'name': item.attr_name,
                'quantity': int(quantity),
                'price': str(item.price),
                'image': preview(item, 'mid')
            }
        else:
            for key, value in self.cart.items():
                if key == str(find_item_id):
                    value['quantity'] = value['quantity'] + int(quantity)
                    value['price'] = str(item.price)
                    newItem = False
                    self.save()
                    break
            if newItem:
                self.cart[find_item_id] = {
                    'userid': self.request.user.id,
                    'item_id': item.pk,
                    'obj': s_item,
                    'name': item.attr_name,
                    'quantity': int(quantity),
                    'price': str(item.price),
                    'image': preview(item, 'mid')
                }
        if newItem:  # save when it is new item
            self.save()

    def save(self):
        # update the session cart
        self.session[settings.CART_SESSION_ID] = self.cart
        if self.request.user.is_authenticated:
            # load items from session and add to database
            for key, value in self.cart.items():
                try:
                    obj_item = CartItem.objects.get(cart_id=self.cart_obj, find_item_id=key)
                except CartItem.DoesNotExist:
                    obj_item = CartItem.objects.create(cart_id=self.cart_obj, find_item_id=key)
                try:
                    _item = next(serializers.deserialize("json", value['obj'])).object if 'obj' in value else None
                    if _item is not None and isinstance(_item, ProductAttribute):
                        obj_item.find_item_id = key
                        obj_item.class_of_item = value['obj']
                        obj_item.name = value['name']
                        obj_item.price = _item.price
                        obj_item.original_price = obj_item.price
                        obj_item.quantity = value['quantity']
                        obj_item.total_price = Decimal(obj_item.price) * value['quantity']
                        obj_item.save()
                except IndexError:
                    break;
            # load items from database and add to session
            items = CartItem.objects.filter(cart_id=self.cart_obj)
            for item in items:
                try:
                    _item = next(serializers.deserialize("json", item.class_of_item)).object if to_python(
                        item.class_of_item) else None
                    if _item is not None and isinstance(_item, ProductAttribute):
                        self.cart[item.find_item_id] = {
                            'userid': self.request.user.id,
                            'item_id': _item.pk,
                            'obj': item.class_of_item,
                            'name': item.name,
                            'quantity': int(item.quantity),
                            'price': str(_item.price),
                            'image': preview(_item, 'mid')
                        }
                except IndexError:
                    break;
        # mark the session as "modified" to make sure it is saved
        self.session.modified = True

    def remove(self, item):
        """
        Remove a item from the cart.
        """
        if isinstance(item, ProductAttribute) and isinstance(self.cart_obj.pk, int):
            find_item_id = "{}_{}".format(self.cart_obj.pk, item.pk)
            try:
                item = CartItem.objects.get(find_item_id=find_item_id)
                item.delete()
            except CartItem.DoesNotExist:
                pass
        elif isinstance(item, CartItem):
            find_item_id = item.pk
            item.delete()
            if find_item_id in self.cart:
                print(self.cart[find_item_id])
        else:
            if isinstance(item, str):
                try:
                    item = CartItem.objects.get(cart_id=self.cart_obj, find_item_id=item)
                    find_item_id = item.pk
                    item.delete()
                except CartItem.DoesNotExist:
                    pass
        if find_item_id in self.cart:
            del self.cart[find_item_id]
        if find_item_id not in self.cart:
            self.session[settings.CART_SESSION_ID] = self.cart
            self.session.modified = True

    def increment(self, item):
        for key, value in self.cart.items():
            if key == str(item.pk):
                value['quantity'] = int(value['quantity']) + 1
                if value['quantity'] < 1:
                    return redirect('cart:cart_detail')
                self.save()
                break
            else:
                print("Something Wrong")

    def decrement(self, item):
        for key, value in self.cart.items():
            if key == str(item.pk):
                value['quantity'] = value['quantity'] - 1
                if value['quantity'] < 1:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                self.save()
                break
            else:
                print("Something Wrong")

    def __iter__(self):
        """
        Iterate over the items in the cart and get the items
        from the database.
        """

        item_ids = self.cart.keys()
        # get the item objects and add them to the cart
        items = CartItem.objects.filter(find_item_id__in=item_ids, cart_id=self.cart_obj)
        cart = self.cart.copy()
        for item in items:
            self.cart[str(item.find_item_id)]['item'] = item
        for item in self.cart.values():
            try:
                _item = next(serializers.deserialize("json", item['obj'])).object if to_python(item['obj']) else None
                if isinstance(_item, ProductAttribute):
                    item['price'] = str(_item.price)
                    item['total_price'] = str(Decimal(item['price']) * item['quantity'])
                yield item
            except IndexError:
                break;

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_total_item(self):
        return len(self.cart.keys())

    def clear(self):
        # empty cart
        self.session[settings.CART_SESSION_ID] = {}
        try:
            objs = CartItem.objects.filter(cart_id=self.cart_obj)
            for obj in objs:
                obj.delete()
        except (CartItem.DoesNotExist, ProtectedError):
            pass
        self.session.modified = True

    def update(self, item, quantity, unit_price=None):
        if isinstance(item, CartItem):
            item = CartItem.objects.filter(cart_id=self.cart_obj, find_item_id=item.pk).first()
        elif isinstance(item, ProductAttribute):
            find_item_id = "{}_{}".format(self.cart_obj.pk, item.pk)
            try:
                item = CartItem.objects.get(find_item_id=find_item_id)
            except CartItem.DoesNotExist:
                item = CartItem.objects.get(find_item_id=find_item_id)
        else:
            try:
                item = CartItem.objects.get(cart_id=self.cart_obj, find_item_id=item) if isinstance(item, str) else None
            except CartItem.DoesNotExist:
                item = None
        if item is not None and isinstance(item, CartItem):
            if quantity == 0:
                item.delete()
            else:
                item.quantity = int(quantity)
                item.save()
        else:
            raise ItemDoesNotExist
