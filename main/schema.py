from spa.utils import get_paginator
from . import models


# Let's assume you have some ObjectType for one of your models:
class ProductType(DjangoObjectType):
    class Meta:
        model = models.Product


# Now we create a corresponding PaginatedType for that object type:
class ProductPaginatedType(graphene.ObjectType):
    page = graphene.Int()
    pages = graphene.Int()
    has_next = graphene.Boolean()
    has_prev = graphene.Boolean()
    objects = graphene.List(ProductType)


class Query(object):
    products = graphene.Field(ProductPaginatedType, page=graphene.Int())

    # Now, in your resolver functions, you just query your objects and turn the queryset into the PaginatedType using the helper function:
    def resolve_products(self, info, page):
        page_size = 10
        qs = models.Product.objects.all()
        return get_paginator(qs, page_size, page, ProductPaginatedType)
