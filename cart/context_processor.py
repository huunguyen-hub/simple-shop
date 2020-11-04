from .mycart import MyCart


def cart_total_amount(request):
    total_bill = 0.0
    _cart = None
    if request.user.is_authenticated:
        cart = MyCart(request)
        _cart = cart.cart_obj if cart is not None else None
        for key, value in cart.cart.items():
            total_bill = total_bill + (float(value['price']) * value['quantity'])
        return {'cart_total_amount': total_bill, 'cart_total_paid_real': total_bill, 'cart_total_wrapping': 0, 'cart': _cart}
    else:
        return {'cart_total_amount': 0, 'cart_total_paid_real': total_bill, 'cart_total_wrapping': 0, 'cart': _cart}

