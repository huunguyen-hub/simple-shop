import json

from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Subquery
from django.http import HttpResponse
# from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.urls import reverse_lazy, reverse
from django.utils.cache import add_never_cache_headers
from django.views import generic
from django.views.generic import ListView, TemplateView
from django.views.generic.detail import BaseDetailView

from spa.utils import decrypt
from .const import SECRET_KEY_CRYPT, TYPE0, TYPE1
from .forms import ContactForm
from .models import FeatureValue, Category, ProductAttribute, ProductAttributeCombination, Product, CategoryProduct, \
    Post, Contact

handler404 = 'main.views.bad_request'


def bad_request(request):
    return redirect(reverse('home'))


def signout(request):
    logout(request)
    return redirect(reverse('home'))


words = ('cart', 'order', 'add', 'del', 'upd', 'rem', 'login', 'sign', 'logout', 'reset')


def signin(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            form = AuthenticationForm(request.POST)
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def get(self, request, *args, **kwargs):
        context = {}
        context.update(csrf(request))
        context['form'] = UserCreationForm()
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        context = {}
        form = context['form'] = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            if request.user.is_authenticated:
                return redirect(reverse('home'))
            else:
                return render(request, template_name=self.template_name, context=context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            next = request.META['PATH_INFO']
            for word in words:
                if next.find(word):
                    return redirect(reverse('home'))
            return redirect('home')
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return render(request, 'registration/signup.html', {'form': form})
    else:
        form = UserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})


def prepare_context(context_data):
    """
    Function that create context data for all Views classes.
    """
    context_data['menu'] = {}
    return context_data


class AjaxLoadBaseView(BaseDetailView):
    def get(self, request, *args, **kwargs):
        field = request.GET.get('field')
        parent_value = request.GET.get("parent_value")
        choices = [(featureval.feature_value_id, featureval.value) for featureval in
                   FeatureValue.objects.all().filter(feature_id=parent_value)]

        response = HttpResponse(
            json.dumps(choices, cls=DjangoJSONEncoder),
            content_type='application/json'
        )
        add_never_cache_headers(response)
        return response


class AjaxCheckView(BaseDetailView):
    def get(self, request, *args, **kwargs):
        pid = request.GET.get('pid')
        cid = request.GET.get('cid')
        values = request.GET.get('values')
        list1 = [int(x) for x in values.split(",")]
        list1.sort()
        context = {
            "pid": pid,
            "cid": cid,
            "values": values,
        }
        curl = None
        try:
            objs = ProductAttribute.objects.filter(product_id=pid).exclude(pk=cid)
            for obj in objs:
                # list_com = ProductAttributeCombination.objects.filter(pro_attribute_id=obj.pk)
                list2 = [com.attribute_id.pk for com in
                         ProductAttributeCombination.objects.filter(pro_attribute_id=obj.pk)]
                list2.sort()
                if list1 == list2:
                    try:
                        curl = obj.get_absolute_url()
                    except AttributeError:
                        raise ImproperlyConfigured("No URL to redirect to.")
                    break
        except (ObjectDoesNotExist, IndexError, ValueError, TypeError):
            curl = None
        context['curl'] = curl
        response = HttpResponse(
            json.dumps(context, cls=DjangoJSONEncoder), content_type='application/json'
        )
        add_never_cache_headers(response)
        return response


class AjaxChainedView(BaseDetailView):
    def get(self, request, *args, **kwargs):
        obj = request.GET.get('field_obj')
        classified = apps.get_model('main', obj)
        child_id = request.GET.get('field')
        child_name = request.GET.get('field_value')
        parent_value = request.GET.get("parent_value")
        parent_field = request.GET.get('parent_field')
        name = "%s__exact" % parent_field
        try:
            list_of_class = ['FeatureValue', 'Attribute', 'City', 'District', 'Ward', 'Address']
            if obj in list_of_class:
                choices = [(getattr(obj, child_id), getattr(obj, child_name)) for obj in
                           classified.objects.all().filter(**{name: parent_value})]
            else:
                choices = [(getattr(obj, child_id), getattr(obj, child_name)) for obj in
                           classified.objects.none()]
        except (ObjectDoesNotExist, IndexError, ValueError, TypeError):
            choices = []

        response = HttpResponse(
            json.dumps(choices, cls=DjangoJSONEncoder), content_type='application/json'
        )
        add_never_cache_headers(response)
        return response


class Dashboard(ListView):
    model = ProductAttribute
    paginate_by = 12
    queryset = ProductAttribute.objects.all()
    context_object_name = 'productattributes'
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat_pros = CategoryProduct.objects.all()
        context['categories'] = Category.objects.filter(category_id__in=Subquery(cat_pros.values('category_id')))
        # for category in context['categories']:
        #     print(category, category.products.all())
        #     pdb.set_trace()
        context['products'] = Product.objects.all()[:5]
        return context

    def get_context_data_backup(self, *, object_list=None, **kwargs):
        """Get the context for this view."""
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        context['categories'] = Category.objects.all()[:4]
        context['products'] = Product.objects.all()[:4]
        return super().get_context_data(**context)


class ContactView(TemplateView):
    template_name = 'pages/contact_form.html'
    paginate_by = 3

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context = prepare_context(context)
        context['categories'] = Category.objects.all()[:4]
        context['posts'] = Post.objects.all()[:self.paginate_by]
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update(csrf(request))
        context['form'] = ContactForm(user=request.user)
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        data = request.POST.copy()
        if request.user.is_authenticated:
            data['name'] = "{} {}".format(request.user.first_name, request.user.last_name)
            data['email'] = "{}".format(request.user.email)
        else:
            return redirect('login')
        form = ContactForm(initial=data, user=request.user, data=data)
        if form.is_valid():
            obj, created = Contact.objects.get_or_create(
                company=form.cleaned_data['company'],
                name="{} {}".format(request.user.first_name,
                                    request.user.last_name) if request.user.is_authenticated else form.cleaned_data[
                    'name'],
                email="{}".format(request.user.email) if request.user.is_authenticated else form.cleaned_data['email'],
                mobile=form.cleaned_data['mobile'],
                description=form.cleaned_data['description'],
                customer_service=form.cleaned_data['customer_service'],
            )
            if obj is not None and isinstance(obj, Contact):
                obj.company = form.cleaned_data['company']
                obj.name = "{} {}".format(request.user.first_name,
                                          request.user.last_name) if request.user.is_authenticated else \
                    form.cleaned_data['name']
                obj.email = "{}".format(request.user.email) if request.user.is_authenticated else form.cleaned_data[
                    'email']
                obj.mobile = form.cleaned_data['mobile']
                obj.description = form.cleaned_data['description']
                obj.customer_service = form.cleaned_data['customer_service']
                obj.save()
                # token = encrypt(obj.pk, SECRET_KEY_CRYPT)
            else:
                created.company = form.cleaned_data['company']
                created.name = "{} {}".format(request.user.first_name,
                                              request.user.last_name) if request.user.is_authenticated else \
                    form.cleaned_data['name']
                created.email = "{}".format(request.user.email) if request.user.is_authenticated else form.cleaned_data[
                    'email']
                created.mobile = form.cleaned_data['mobile']
                created.description = form.cleaned_data['description']
                created.customer_service = form.cleaned_data['customer_service']
                created.save()
                # token = encrypt(created.pk, SECRET_KEY_CRYPT)
            # send {'token'} to email or mobile to verify
            return redirect('home')

        context['form'] = form
        return render(request, template_name=self.template_name, context=context)


def contact_verify(request, token):
    pk = decrypt(token, SECRET_KEY_CRYPT)
    obj = Contact.objects.get(pk=pk)
    if obj is not None and obj.status == TYPE0:
        obj.status = TYPE1
        obj.save()
    return redirect('home')
