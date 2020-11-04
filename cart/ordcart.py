from main.models import CartItem, ProductAttribute, Cart, Order, OrderItem, OrderState
from spa.utils import rand_word


class ItemAlreadyExists(Exception):
    pass


class ItemDoesNotExist(Exception):
    pass


class OrdCart(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        if request.user.is_authenticated:
            current_user = request.user
            try:
                cart_obj = Cart.objects.get(owner=current_user)
                self.cart_obj = cart_obj
                try:
                    order_obj = Order.objects.get(owner=current_user, cart_id=cart_obj)
                except Order.DoesNotExist:
                    secure_key = rand_word(8)
                    current_state = OrderState.objects.get(pk=1)
                    order_obj = Order.objects.create(owner=current_user, cart_id=cart_obj, secure_key=secure_key,
                                                     current_state=current_state)
                self.order_obj = order_obj
            except (Cart.DoesNotExist, Order.DoesNotExist):
                pass

    def get_items(self):
        return OrderItem.objects.filter(order_id=self.order_obj)

    def reload(self, cart=None):
        if cart is None or not isinstance(cart, Cart):
            cart = self.cart_obj
        items = CartItem.objects.filter(cart_id=cart.pk)
        find_item_ids = []
        for item in items:
            find_item_id = "{}_{}".format(self.order_obj.pk, item.find_item_id)
            find_item_ids.append(find_item_id)
            try:
                _item = OrderItem.objects.get(pk=find_item_id)
            except (OrderItem.DoesNotExist, CartItem.DoesNotExist):
                _item = OrderItem.objects.create(order_id=self.order_obj, find_item_id=find_item_id)
            _item.class_of_item = item.class_of_item
            _item.name = item.name
            _item.quantity = item.quantity
            _item.unity = item.unity
            _item.price = item.price
            _item.original_price = item.original_price
            _item.total_price = item.total_price
            _item.save()
        _items = self.get_items()
        for _item in _items:
            if _item.pk not in find_item_ids:
                _item.delete()
        self.save()

    def load(self, cart=None):
        if cart is None or not isinstance(cart, Cart):
            cart = self.cart_obj
        items = CartItem.objects.filter(cart_id=cart.pk)
        for item in items:
            find_item_id = "{}_{}".format(self.order_obj.pk, item.find_item_id)
            try:
                _item = OrderItem.objects.get(pk=find_item_id)
            except (OrderItem.DoesNotExist, CartItem.DoesNotExist):
                _item = OrderItem.objects.create(order_id=self.order_obj, find_item_id=find_item_id)
            _item.class_of_item = item.class_of_item
            _item.name = item.name
            _item.quantity = item.quantity
            _item.unity = item.unity
            _item.price = item.price
            _item.original_price = item.original_price
            _item.total_price = item.total_price
            _item.save()

    def add(self, item, quantity=1, action=None):
        """
        Add a item to the cart or update its quantity.
        """
        find_item_id = "{}_{}".format(self.order_obj.pk, item.find_item_id)
        try:
            _item = OrderItem.objects.get(find_item_id=find_item_id)
        except CartItem.DoesNotExist:
            _item = OrderItem.objects.create(order_id=self.order_obj, find_item_id=find_item_id)
        _item.class_of_item = item.class_of_item
        _item.name = item.name
        _item.quantity = item.quantity
        _item.unity = item.unity
        _item.price = item.price
        _item.original_price = item.original_price
        _item.total_price = item.total_price
        _item.save()

    def save(self):
        items = OrderItem.objects.filter(order_id=self.order_obj)
        total_paid = 0
        total_wrapping = 0
        for item in items:
            total_paid += item.quantity*item.price
        total_paid_real = total_paid
        self.order_obj.total_wrapping = total_wrapping
        self.order_obj.total_paid = total_paid
        self.order_obj.total_paid_real = total_paid_real
        self.order_obj.save()
        self.session.modified = True

    def remove(self, item):
        """
        Remove a item from the cart.
        """
        if isinstance(item, ProductAttribute) and isinstance(self.order_obj.pk, int):
            find_item_id = "{}_{}".format(self.order_obj.pk, item.pk)
            try:
                item = OrderItem.objects.get(find_item_id=find_item_id)
                item.delete()
            except OrderItem.DoesNotExist:
                pass
        elif isinstance(item, OrderItem):
            item.delete()
        else:
            if isinstance(item, str):
                try:
                    item = OrderItem.objects.get(cart_id=self.order_obj, find_item_id=item)
                    item.delete()
                except OrderItem.DoesNotExist:
                    pass

    def increment(self, item):
        item.quantity += 1
        item.save()

    def decrement(self, item):
        item.quantity -= 1
        if item.quantity > 0:
            item.save()
