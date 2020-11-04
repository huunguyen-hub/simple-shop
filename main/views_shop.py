from django.http import Http404
from django.shortcuts import render
from django.views.generic import ListView, DetailView

from main.models import ProductAttribute, Product, FeatureProduct, Category
from main.views import prepare_context


class ProductView(ListView):
    model = ProductAttribute
    paginate_by = 15
    context_object_name = 'productattributes'
    template_name = 'shop/product.html'

    def get_queryset(self):
        if 'pk' in self.kwargs:
            return ProductAttribute.objects.filter(product_id=self.kwargs['pk'])
        else:
            return ProductAttribute.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = prepare_context(context)
        if 'pk' in self.kwargs:
            model = Product.objects.get(product_id=self.kwargs['pk'])
            context['model'] = model

        context['categories'] = Category.objects.all()[:4]
        context['products'] = Product.objects.all()[:4]

        categories = Category.objects.all()[:4]
        products = Product.objects.all()[:4]
        context['group'] = zip(categories, products)

        return context


class ProductAtributeView(DetailView):
    model = ProductAttribute
    template_name = 'shop/product_detail.html'
    """
    A base view for displaying a single object
    """

    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     context = self.get_context_data(object=self.object)
    #     return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = prepare_context(context)
        context['categories'] = Category.objects.all()[:4]
        context['products'] = Product.objects.all()[:4]
        context['model'] = ProductAttribute.objects.get(pk=self.object.pk)
        if context['model'] is not None:
            obj = context['model']
            context['obj_features'] = FeatureProduct.objects.filter(product_id=obj.product_id).order_by('-feature_id',
                                                                                                        'feature_value_id')
            context['obj_attributes'] = obj.attributes.all()

            context['models'] = ProductAttribute.objects.filter(product_id=obj.product_id)
        else:
            context['models'] = ProductAttribute.objects.all()[:4]
        return context


class ShopView(ListView):
    model = ProductAttribute
    paginate_by = 8
    queryset = ProductAttribute.objects.all()
    context_object_name = 'productattributes'
    template_name = 'shop/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = prepare_context(context)
        context['categories'] = Category.objects.all()[:4]
        context['products'] = Product.objects.all()[:4]
        return context


def get_detail(request, pk):
    try:
        pks = pk.split("_")
    except ProductAttribute.DoesNotExist:
        raise Http404('pk does not exist')

    return render(request, 'shop/details.html',
                  context={'pks': pks})
