import os
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.http import HttpResponse
from django.http import HttpResponseRedirect, Http404, FileResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView, View

from cart.mycart import MyCart
from cart.ordcart import OrdCart
from main.const import METHOD_PAYMENT1, TYPE1, IMGCON_TYPES, DOCCON_TYPES, MAX_SIZE_UPLOADED
from main.forms import AddressForm, OrderPaymentForm
from main.models import ProductAttribute, CartItem, Cart, Order, Address, OrderInvoicePayment, OrderPayment, \
    OrderInvoice
from spa.utils import save_file, save_image


@login_required(login_url="/login")
def txt_view(request, pk, name):
    fullname = None
    try:
        model = OrderPayment.objects.get(pk=pk)
        if isinstance(model.CONST_TYPE, str) or isinstance(model.pk, int):
            folder = "{}/{}".format(model.CONST_TYPE, model.pk)
            path = settings.MEDIA_ROOT + '/' + folder
            fullname = path + '/' + name + ".txt"
    except OrderPayment.DoesNotExist:
        return redirect("main:shop")
    try:
        if fullname is None or not os.path.exists(fullname):
            raise Exception("Request not exist")
        else:
            # deepcode ignore PT: <please specify a reason of ignoring this>
            with open(fullname, 'rb') as fo:
                response = HttpResponse(fo.read(), content_type='text/plain')
                response['Content-Disposition'] = 'inline;{}.txt'.format('name')
                return response
            pdf.closed
    except (ValueError, FileNotFoundError):
        try:
            return FileResponse(open(fullname, 'rb'), content_type='text/plain')
        except FileNotFoundError:
            response = render(request, '404.html', )
            response.status_code = 404
            return response


class DisplayPDFView(View):
    def get_context_data(self, **kwargs):  # Exec 1st
        # context = super().get_context_data(**kwargs)
        context = {}
        if 'name' in self.kwargs and 'pk' in self.kwargs:
            model = OrderPayment.objects.get(pk=self.kwargs['pk'])
            context['model'] = model
            if model is not None and isinstance(model.CONST_TYPE, str) or isinstance(model.pk, int):
                folder = "{}/{}".format(model.CONST_TYPE, model.pk)
                path = settings.MEDIA_ROOT + '/' + folder
                path_url = settings.MEDIA_URL + folder
                if not re.search("^[a-zA-Z0-9]+$", self.kwargs['name']):
                    return context
                fullname = path + '/' + self.kwargs['name'] + ".pdf"
                fullname_url = path_url + '/' + self.kwargs['name'] + ".pdf"
                context['fullname'] = fullname
                context['fullname_url'] = fullname_url
                context['name'] = self.kwargs['name']
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        try:
            if 'fullname' not in context or not os.path.exists(context['fullname']):
                raise Exception("Request not exist")
            else:
                with open(context['fullname'], 'rb') as pdf:
                    response = HttpResponse(pdf.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'inline;{}.pdf'.format(context['name'])
                    return response
                pdf.closed
        except (ValueError, FileNotFoundError):
            try:
                return FileResponse(open(context['fullname'], 'rb'), content_type='application/pdf')
            except FileNotFoundError:
                response = render(request, '404.html', )
                response.status_code = 404
                return response


# Remove login_required if view open to public
display_pdf_view = login_required(DisplayPDFView.as_view())


@login_required(login_url="/login")
def cart_add(request, pk):
    cart = MyCart(request)
    try:
        product = ProductAttribute.objects.get(pro_attribute_id=pk)
        cart.add(item=product)
    except Cart.DoesNotExist:
        cart_item = CartItem.objects.get(find_item_id=pk)
        cart.add(item=cart_item)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="/login")
def cart_clear(request, pk):
    cart = MyCart(request)
    try:
        item = CartItem.objects.get(find_item_id=pk)
        cart.remove(item)
    except CartItem.DoesNotExist:
        return redirect("main:shop")

    if cart.get_total_item() > 0:
        order = OrdCart(request)
        if isinstance(order.order_obj, Order):
            order.reload(cart.cart_obj)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect("main:shop")


@login_required(login_url="/login")
def cart_increment(request, pk):
    cart = MyCart(request)
    product = ProductAttribute.objects.get(pro_attribute_id=pk)
    cart.add(item=product)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="/login")
def cart_decrement(request, pk):
    cart = MyCart(request)
    product = ProductAttribute.objects.get(pro_attribute_id=pk)
    cart.decrement(item=product)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="/login")
def cart_reset(request):
    cart = MyCart(request)
    cart.clear()
    order = OrdCart(request)
    if isinstance(order.order_obj, Order):
        order.reload(cart.cart_obj)
    return redirect("main:shop")


@login_required(login_url="/login")
def cart_detail(request):
    cart = MyCart(request)
    if cart.get_total_item() <= 0:
        return redirect("main:shop")
    else:
        return render(request, 'cart/index.html')


@login_required(login_url="/login")
def cart_update(request):
    cart = MyCart(request)
    if cart.get_total_item() <= 0:
        return redirect("main:shop")
    else:
        return render(request, 'cart/index.html')


@login_required(login_url="/login")
def cart_process(request, pk=None, act=None):
    cart = MyCart(request)
    if cart.get_total_item() <= 0:
        return redirect("main:shop")
    else:
        order = OrdCart(request)
        if not isinstance(order.order_obj, Order):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.load(cart.cart_obj)
        return render(request, 'order/index.html', {'order': order.order_obj, 'items': order.get_items()})


@login_required(login_url="/login")
def order_delivery(request, pk=None):
    cart = MyCart(request)
    if cart.get_total_item() <= 0:
        return redirect("main:shop")
    else:
        order = OrdCart(request)
        if not isinstance(order.order_obj, Order):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.load(cart.cart_obj)
        if request.is_ajax():
            template_name = 'order/address_inner.html'
        else:
            template_name = 'order/delivery.html'
        object = order.order_obj.address_delivery if isinstance(order.order_obj.address_delivery, Address) else None
        if object is None and cart.cart_obj.address is not None:
            object = cart.cart_obj.address
            object.pk = None
        if request.method == 'POST':
            form = AddressForm(instance=object, data=request.POST) if object is not None else AddressForm(
                data=request.POST)
            if form.is_valid():
                if order.order_obj.address_delivery is None:
                    address = form.save()
                    order.order_obj.address_delivery = address
                    order.order_obj.save()
                else:
                    address = order.order_obj.address_delivery
                    address.address = form.cleaned_data['address']
                    address.mobile = form.cleaned_data['mobile']
                    address.city_id = form.cleaned_data['city_id']
                    address.district_id = form.cleaned_data['district_id']
                    address.ward_id = form.cleaned_data['ward_id']
                    address.save()

                if not request.is_ajax() and 'delivery' in request.POST and request.POST['delivery'] == 'invoice':
                    if not isinstance(order.order_obj.address_invoice, Address) and isinstance(
                            order.order_obj.address_delivery, Address):
                        obj = Address.objects.get(pk=address.pk)
                        obj.pk = None
                        obj.save()
                        order.order_obj.address_invoice = obj
                        order.order_obj.save()
                    if isinstance(order.order_obj.address_delivery, Address) and cart.cart_obj.address is None:
                        obj = Address.objects.get(pk=address.pk)
                        obj.pk = None
                        obj.save()
                        cart.add_address(obj)
                    return redirect("cart:order_invoice", pk)
                if not request.is_ajax() and 'delivery' in request.POST and request.POST['delivery'] == 'payment':
                    return redirect("cart:order_payment", pk)
                if not request.is_ajax():
                    next = request.META['PATH_INFO']
                    return HttpResponseRedirect(next)
        else:
            form = AddressForm() if object is None else AddressForm(instance=object)
        return render(request, template_name, {'order': order.order_obj, 'items': order.get_items(), 'form': form})


@login_required(login_url="/login")
def order_invoice(request, pk=None):
    cart = MyCart(request)
    if cart.get_total_item() <= 0:
        return redirect("main:shop")
    else:
        order = OrdCart(request)
        if not isinstance(order.order_obj, Order):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.load(cart.cart_obj)
        if request.is_ajax():
            template_name = 'order/address_inner.html'
        else:
            template_name = 'order/invoice.html'
        object = order.order_obj.address_invoice if isinstance(order.order_obj.address_invoice, Address) else None
        if request.method == 'POST':
            form = AddressForm(instance=object, data=request.POST) if object is not None else AddressForm(
                data=request.POST)
            if form.is_valid():
                if order.order_obj.address_invoice is None:
                    address = form.save()
                    order.order_obj.address_invoice = address
                    order.order_obj.save()
                else:
                    address = order.order_obj.address_invoice
                    address.address = form.cleaned_data['address']
                    address.mobile = form.cleaned_data['mobile']
                    address.city_id = form.cleaned_data['city_id']
                    address.district_id = form.cleaned_data['district_id']
                    address.ward_id = form.cleaned_data['ward_id']
                    address.save()

                if not request.is_ajax() and 'invoice' in request.POST and request.POST['invoice'] == 'delivery':
                    if isinstance(order.order_obj.address_invoice, Address) and not isinstance(
                            order.order_obj.address_delivery, Address):
                        obj = Address.objects.get(pk=address.pk)
                        obj.pk = None
                        obj.save()
                        order.order_obj.address_delivery = obj
                        order.order_obj.save()
                    return redirect("cart:order_delivery", pk)
                if not request.is_ajax() and 'invoice' in request.POST and request.POST['invoice'] == 'payment':
                    return redirect("cart:order_payment", pk)
                if not request.is_ajax():
                    next = request.META['PATH_INFO']
                    return HttpResponseRedirect(next)
        else:
            form = AddressForm() if object is None else AddressForm(instance=object)
        return render(request, template_name, {'order': order.order_obj, 'items': order.get_items(), 'form': form})


@login_required(login_url="/login")
def order_payment(request, pk=None):
    cart = MyCart(request)
    if cart.get_total_item() <= 0:
        return redirect("main:shop")
    else:
        order = OrdCart(request)
        if not isinstance(order.order_obj, Order):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.reload(cart.cart_obj)
        if not isinstance(order.order_obj.address_delivery, Address):
            return redirect("cart:order_delivery", pk)
        if not isinstance(order.order_obj.address_invoice, Address):
            return redirect("cart:order_invoice", pk)
        else:
            try:
                invoice = OrderInvoice.objects.get(order_id=order.order_obj)
            except OrderInvoice.DoesNotExist:
                invoice = OrderInvoice.objects.create(order_id=order.order_obj)
            invoice.amount = order.order_obj.total_paid_real
            invoice.note = "Auto general in process payment"
            invoice.save()
            mid_obj = None
            max_loop = 1
            while mid_obj is None and max_loop >= 0:
                try:
                    mid_obj = OrderInvoicePayment.objects.get(order_id=order.order_obj, order_invoice_id=invoice)
                    object = mid_obj.order_payment_id
                except (OrderInvoicePayment.DoesNotExist, OrderPayment.DoesNotExist):
                    object = OrderPayment.objects.create(amount=order.order_obj.total_paid_real,
                                                         payment_method=METHOD_PAYMENT1,
                                                         order_reference=order.order_obj.secure_key)
                    mid_obj = OrderInvoicePayment.objects.create(order_payment_id=object, order_id=order.order_obj,
                                                                 order_invoice_id=invoice, sign=TYPE1)
                max_loop -= 1
                object.amount = order.order_obj.total_paid_real
                object.payment_method = METHOD_PAYMENT1 if object.payment_method is None else object.payment_method
                object.save()
            if request.method == 'POST':
                form = OrderPaymentForm(instance=object, data=request.POST) if object is not None else OrderPaymentForm(
                    data=request.POST)
                if form.is_valid():
                    object.order_reference = order.order_obj.secure_key
                    object.amount = form.cleaned_data['amount']
                    object.payment_method = form.cleaned_data['payment_method']
                    object.data_payment = form.cleaned_data['data_payment']
                    object.save()
                    for i in range(1, MAX_SIZE_UPLOADED + 1):
                        name = "file%s" % i
                        _file = request.FILES[name] if name in request.FILES else False
                        if _file is not None and (
                                isinstance(_file, InMemoryUploadedFile) or isinstance(_file, TemporaryUploadedFile)):
                            try:
                                con_type = _file.content_type
                                if con_type in IMGCON_TYPES:
                                    save_image(request, object)
                                elif con_type in DOCCON_TYPES:
                                    save_file(request, object)
                                else:
                                    continue
                            except (AttributeError, IndexError, ValueError):
                                continue
                    if not request.is_ajax() and 'payment' in request.POST and request.POST['payment'] == 'finished':
                        return redirect("cart:order_process", pk)
                    if not request.is_ajax():
                        next = request.META['PATH_INFO']
                        return HttpResponseRedirect(next)
            else:
                form = OrderPaymentForm() if object is None else OrderPaymentForm(instance=object)
            template_name = 'order/payment.html'
            return render(request, template_name,
                          {'order': order.order_obj, 'items': order.get_items(), 'form': form, 'object': object})


def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404


@login_required(login_url="/login")
def order_process(request, pk=None):
    cart = MyCart(request)
    if cart.get_total_item() <= 0:
        return redirect("main:shop")
    else:
        order = OrdCart(request)
        if not isinstance(order.order_obj, Order):
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        order.reload(cart.cart_obj)
        if not isinstance(order.order_obj.address_delivery, Address):
            return redirect("cart:order_delivery", pk)
        if not isinstance(order.order_obj.address_invoice, Address):
            return redirect("cart:order_invoice", pk)
        else:
            try:
                invoice = OrderInvoice.objects.get(order_id=order.order_obj)
                OrderInvoicePayment.objects.get(order_id=order.order_obj, order_invoice_id=invoice)
                order.order_obj.cart_id = None
                order.order_obj.save()
                cart.clear()
            except (OrderInvoice.DoesNotExist, OrderInvoicePayment.DoesNotExist, OrderPayment.DoesNotExist):
                return redirect("cart:order_payment", pk)

            template_name = 'order/success.html'
            return render(request, template_name,
                          {'order': order.order_obj})


class CartProcessView(TemplateView):
    model = CartItem
    context_object_name = 'item'
    template_name = 'order/index.html'

    def get(self, request, *args, **kwargs):
        """
        return regular list view on page load and then json data on
        datatables ajax request.
        """
        cart = MyCart(request)
        if cart.get_total_item() <= 0:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            order = OrdCart(request)
            if not isinstance(order.order_obj, Order):
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                order.load(cart.cart_obj)
        context = super(CartProcessView, self).get_context_data(**kwargs)
        context['order'] = order.order_obj
        context['items'] = order.get_items()
        return self.render_to_response(context)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['cart'] = Cart.objects.get(pk=self.kwargs['pk'])
        context['item'] = CartItem.objects.filter(cart_id=context['cart'])
        return context


class OrderListView(ListView):
    model = Order


class OrderDetailView(DetailView):
    model = Order
