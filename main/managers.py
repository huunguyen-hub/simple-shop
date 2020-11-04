# -*- coding: utf-8 -*-
from django.db import models


class CartManager(models.Manager):
    # creating a new cart or getting the current one
    def new_or_get(self, request):
        cart_obj = None
        if request.user.is_authenticated:
            qs = self.get_queryset().filter(id_owner=request.user)
            cart_obj = qs.first()
            if cart_obj.id_owner is None:
                cart_obj.id_owner = request.user
                cart_obj.save()
            return cart_obj
        else:
            return cart_obj

    # Associating the user to the cart
    def new(self, user=None):
        cart_obj = None
        if user is not None and user.is_authenticated:
            user_obj = user
            cart_obj = self.model.objects.create(owner=user_obj)
        return user_obj


class Cart_Manager(object):
    # creating a new cart or getting the current one
    def new_or_get(self, request):
        cart_obj = None
        if request.user.is_authenticated:
            qs = self.get_queryset().filter(owner=request.user)
            cart_obj = qs.first()
            if cart_obj.owner is None:
                cart_obj.owner = request.user
                cart_obj.save()
            return cart_obj
        else:
            return cart_obj

    # Associating the user to the cart
    def new(self, user=None):
        cart_obj = None
        if user is not None and user.is_authenticated:
            user_obj = user
            cart_obj = self.model.objects.create(owner=user_obj)
        return user_obj

