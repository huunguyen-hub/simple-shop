import json
import pdb

from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Subquery
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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
from .views import prepare_context

handler404 = 'main.views.bad_request'


def bad_request(request):
    return redirect(reverse('home'))


class ServiceView(ListView):
    model = ProductAttribute
    paginate_by = 8
    queryset = ProductAttribute.objects.all()
    context_object_name = 'productattributes'
    template_name = 'service/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = prepare_context(context)
        context['categories'] = Category.objects.all()[:4]
        context['products'] = Product.objects.all()[:4]
        return context
