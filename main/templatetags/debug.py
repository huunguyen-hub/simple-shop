# -*- coding: utf-8 -*-
# http://djangosnippets.org/snippets/1550/
#
import pdb
import pdb as pdb_module

from django.template import Library, Node

register = Library()


class PdbNode(Node):

    def render(self, context):
        pdb_module.set_trace()
        return ''


# https://dzone.com/articles/putting-breakpoints-html
@register.tag
def pdb(parser, token):
    return PdbNode()


@register.filter
def ipdb(element):
    pdb.set_trace()
    return element
