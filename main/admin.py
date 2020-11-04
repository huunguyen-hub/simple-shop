import ast
import json
import os
# import nested_admin
from functools import partial

from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.staticfiles.finders import find
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.db.models import Count
from django.forms.models import BaseModelFormSet, BaseInlineFormSet
from django.template.defaultfilters import truncatechars
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from main.const import IMG_EXT_WITH_DOT
from main.forms_admin import PostAdminForm, CategoryAdminForm, ProductAdminForm, ManufacturerAdminForm, LookupAdminForm, \
    FeatureAdminForm, FeatureValueAdminForm, FeatureProductAdminForm, CityAdminForm, ProductAttributeAdminForm, \
    AttributeGroupAdminForm, ProductAttributeGroupAdminForm, ProductAttributeInlineForm, AddressInlineForm
from main.models import Post, Category, Product, Manufacturer, Lookup, Feature, FeatureValue, \
    FeatureProduct, Tag, City, District, Ward, ProductAttribute, AttributeGroup, Attribute, \
    ProductAttributeGroup, ProductAttributeCombination, Profile
from spa import settings
from spa.utils import to_python, isSubArray, save_photo_formset, thumbnail, slider, save_photo, is_json, \
    generate_slug, del_photo, get_max_combined, get_list_combined, get_list_attributes, check_exist_in_dict, \
    proccess_photo


class AddressInline(admin.ModelAdmin):
    # model = Address
    form = AddressInlineForm


class ProfileInline(NestedStackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    # fk_name = 'user'
    fields = (
        'address',
        ('location', 'birth_date'),
        ('role', 'verified', 'social_joined'),
        ('gender', 'couple_status',),
    )


class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class ServerFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(ServerFormSet, self).__init__(*args, **kwargs)
        self.initial = []  # [{ 'name': 's1', }, {'name': 's2'},] # supply your list here


class ServerInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(ServerInlineFormSet, self).__init__(*args, **kwargs)
        self.initial = []  # [{ 'name': 's1', }, {'name': 's2'},] # supply your list here


# https://github.com/django-oscar/django-oscar/issues/1743
class AttributeInline(NestedStackedInline):
    model = Attribute
    extra = 1


@admin.register(AttributeGroup)
class AttributeGroupAdmin(NestedModelAdmin):
    form = AttributeGroupAdminForm
    inlines = [AttributeInline]
    list_display = ('name', 'public_name', 'group_type', 'total_attributes')
    list_filter = ('name', 'public_name', 'group_type',)
    search_fields = ('name', 'public_name',)
    ordering = ('name', 'public_name')
    list_per_page = 50

    @mark_safe
    def total_attributes(self, obj):
        total = 0
        return 'Total attributes %d' % total

    total_attributes.short_description = "Total Of Attributes"


@admin.register(ProductAttributeGroup)
class ProductAttributeGroupAdmin(admin.ModelAdmin):
    form = ProductAttributeGroupAdminForm
    list_display = ('name_of_product', 'name_of_group', 'value_of_attribute')
    ordering = ('product_id', 'attr_group_id', 'attribute_id',)
    list_per_page = 50
    readonly_fields = []
    actions = ['delete_model']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
            obj_pro = obj.product_id
            obj.delete()
            obj_pro.reload_config()
        # queryset.delete()

    def delete_model(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
            obj_pro = obj.product_id
            obj.delete()
            obj_pro.reload_config()

    class Media:
        js = ('/static/js/inline_handlers.js',)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(ProductAttributeGroupAdmin, self).get_readonly_fields(request, obj)
        if obj and obj.pk is not None:
            return readonly_fields  # + ['product_id']
        else:
            return readonly_fields

    @mark_safe
    def name_of_product(self, obj):
        return obj.product_id.name

    @mark_safe
    def name_of_group(self, obj):
        return "%s" % obj.attr_group_id.name

    @mark_safe
    def value_of_attribute(self, obj):
        instObjs = ProductAttributeGroup.objects.filter(product_id=obj.product_id,
                                                        attr_group_id=obj.attr_group_id)
        value_of_alts = "{} in [ ".format(obj.attribute_id.name)
        i = 0
        for instObj in instObjs:
            if i == len(instObjs) - 1:
                value_of_alts += instObj.attribute_id.name
            else:
                value_of_alts += instObj.attribute_id.name + ", "
            i += 1
        value_of_alts += " ]"
        return value_of_alts


class ProductAttributeCombinationInline(NestedTabularInline):
    model = ProductAttributeCombination
    verbose_name = "Attribute Combination In The Product"
    verbose_name_plural = "Attribute Combinations Of Product"
    extra = 2


class ProductAttributeInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        parent = kwargs.get('instance')
        if 'initial' not in kwargs:
            kwargs['initial'] = []
        if isinstance(parent, Product) and parent.pk is not None:
            keys_remove = []
            product_attributes = ProductAttribute.objects.filter(product_id=parent)
            data = ast.literal_eval(to_python(parent.config))
            # remove all combine in config exist in database
            for product_attribute in product_attributes:
                attributes = ProductAttributeCombination.objects.filter(pro_attribute_id=product_attribute)
                str_value = ""
                array_values = []
                for attribute in attributes:
                    str_value += "{}:{}, ".format(attribute.attribute_id.pk, attribute.attribute_id.name)
                    array_values.append(attribute.attribute_id.pk)
                if len(str_value) > 0 or len(array_values) > 0:
                    # find key in config[] and remove it
                    if isinstance(data, dict) and len(list(data.keys())) > 0:
                        try:
                            # tmp_key = str(0)  # find max in list key
                            for key in list(data.keys()):
                                if isSubArray(list(data[key]), array_values):
                                    keys_remove.append(key)
                        except (ValueError, TypeError, IndexError):
                            pass

            if len(kwargs['initial']) <= 0 and isinstance(parent.config, str):
                try:
                    data = ast.literal_eval(to_python(parent.config))
                    if isinstance(data, dict) and len(list(data.keys())) > 0:
                        for key in list(data.keys()):
                            if key in keys_remove: continue
                            str_value = ""
                            for item in data.get(key):
                                attribute = Attribute.objects.get(pk=int(item))
                                str_value += "{}:{}, ".format(item, attribute.name)
                            # kwargs['initial'].insert(0,{'combination': (key, str_value)})
                            kwargs['initial'].append({'combination': (key, str_value)})
                except (ValueError, TypeError, IndexError):
                    pass
        else:
            kwargs['initial'] = []
            kwargs['initial'].append({'combination': ('', '--Choice One Item--')})
        super(ProductAttributeInlineFormSet, self).__init__(*args, **kwargs)

        # nghien cuu set du lieu ban dau o day ????? by huunguyen
        # https://github.com/django-oscar/django-oscar/issues/1743
        # # This return initial [{'attribute' initial}, {..}, {..}]
        # self.initial = [{'attribute': a} for a in obj.category.attributes.all()]
        # # Now we need to make a queryset to each field of each form inline
        # self.queryset = [{'value_option'..}, {..}]

    def is_valid(self):
        instance = getattr(self, 'instance', None)
        result = super().is_valid()
        if self.is_bound:
            for form in self.forms:
                data = form.cleaned_data
                valid = False
                if 'DELETE' in data and data['DELETE']:
                    valid = True
                elif data['attr_name'] is None:
                    valid = False
                else:
                    if instance.config is not None and isinstance(instance.config, str) and is_json(instance.config):
                        config = ast.literal_eval(to_python(instance.config))
                        try:
                            if 'combination' in data and int(data['combination']) >= 0 and data[
                                'combination'] in config:
                                valid = True
                        except ValueError:
                            valid = True
                if not valid:
                    result = result and valid
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        result = super().save(commit=commit)
        instance = getattr(self, 'instance', None)
        for form in self.forms:
            data = form.cleaned_data
            if instance.config is not None and isinstance(instance.config, str) and is_json(instance.config):
                config = ast.literal_eval(to_python(instance.config))
                id_pro_att = data['pro_attribute_id'] if 'pro_attribute_id' in data else False
                com_val = data['combination'] if 'combination' in data else False
                file_in_memory = data['file'] if 'file' in data else False
                if id_pro_att and com_val and file_in_memory:
                    save_photo_formset(data, id_pro_att)
                if com_val in config:
                    if not id_pro_att or not isinstance(id_pro_att, ProductAttribute):
                        id_pro_att = form.save(commit=False)
                        id_pro_att.save()
                        if not isinstance(id_pro_att, ProductAttribute):
                            continue
                    try:
                        if isinstance(id_pro_att, ProductAttribute) and com_val in config:
                            id_pro_att.attributes.through.objects.filter(pro_attribute_id=id_pro_att.pk).delete()
                            for item in config.get(str(com_val)):
                                attribute = Attribute.objects.get(pk=int(item))
                                id_pro_att.attributes.add(attribute)
                                id_pro_att.save()
                    except (ValueError, TypeError, IndexError):
                        continue

            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)
        return result

    def clean(self):
        result = super(ProductAttributeInlineFormSet, self).clean()
        instance = getattr(self, 'instance', None)
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            data = form.cleaned_data
            valid = False
            if 'DELETE' in data and data['DELETE']:
                valid = True
            else:
                if instance.config is not None and isinstance(instance.config, str) and is_json(instance.config):
                    config = ast.literal_eval(to_python(instance.config))
                    try:
                        if 'combination' in data and int(data['combination']) >= 0 and data['combination'] in config:
                            valid = True
                    except ValueError:
                        valid = True
                if data['attr_name'] in [None, ''] and instance is not None and isinstance(instance.name, str):
                    data['attr_name'] = "{} {}".format(instance.name, generate_slug(8))
            if not valid:
                raise forms.ValidationError("A Combination is a string has len() >=0.")
        return result


class ProductAttributeInline(NestedTabularInline):
    formset = ProductAttributeInlineFormSet
    model = ProductAttribute
    _parent_instance = None
    verbose_name = "ProductAttribute Of The Product"
    verbose_name_plural = "ProductAttributes Of The Product"
    # readonly_fields = ['product_id', ]
    readonly_fields = ["headshot"]

    @mark_safe
    def headshot(self, obj):
        return format_html(thumbnail(obj, 'sm'))

    headshot.short_description = 'Image'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name not in ['attr_name', 'price', 'quantity']:  # Override the position widget to be a HiddenInput
            kwargs['widget'] = forms.HiddenInput()
        formfield = super(ProductAttributeInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        return formfield

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ProductAttributeInline, self).get_formset(request, obj, **kwargs)
        formset.request = request

        def formfield_callback(field, **kwargs):
            formfield = field.formfield(**kwargs)
            if field.name == 'pro_attribute_id':
                formfield.queryset = ProductAttribute.objects.filter(product_id=self._parent_instance)
            return formfield

        if self._parent_instance is not None:
            kwargs['formfield_callback'] = formfield_callback
        choices = (('', '--Choice One Item--'),)
        if isinstance(obj, Product) and isinstance(obj.config, str):
            try:
                data = ast.literal_eval(to_python(obj.config))
                if isinstance(data, dict) and len(list(data.keys())) > 0:
                    items = get_list_attributes(obj)
                    for key in data:
                        str_value = ""
                        values = data.get(key)
                        if check_exist_in_dict(values, items):
                            continue
                        for item in values:
                            attribute = Attribute.objects.get(pk=int(item))
                            str_value += "{}:{}, ".format(item, attribute.name)
                        option = (key, str_value)
                        choices += (option,)
            except (ValueError, TypeError, IndexError):
                choices = (('', '--Choice One Item--'),)
        ProductAttributeInline.form = type('ProductAttributeInlineForm', (ProductAttributeInlineForm,), {
            'combination': forms.ChoiceField(label="Combination", choices=choices, required=True)})
        return formset

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ProductAttributeInline, self).get_fieldsets(request, obj)
        new_fieldsets = list(fieldsets)
        # new_dynamic_fields = None  # ['combination', ] them duoc o day nhung chua dac ta loai fields
        # if new_dynamic_fields is not None:
        #     new_fieldsets.append(['Dynamic Fields', {'fields': new_dynamic_fields}])
        return new_fieldsets

    def get_extra(self, request, obj=None, **kwargs):
        extra = super(ProductAttributeInline, self).get_extra(request, obj, **kwargs)
        max_num = get_max_combined(obj)
        return max_num if obj and isinstance(max_num, int) else extra

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = get_max_combined(obj)
        if obj.product_id is not None and isinstance(obj.product_id, int):
            product = Product.objects.get(pk=obj.product_id)
            if isinstance(product, Product) and isinstance(obj.config, str):
                try:
                    data = ast.literal_eval(to_python(product.config))
                    if isinstance(data, dict) and len(list(data.keys())) > 0:
                        max_num = len(list(data.keys()))
                    else:
                        items = get_list_combined(product)
                        product.config = json.dumps(items, cls=DjangoJSONEncoder)
                        product.save()
                except (ValueError, TypeError, IndexError):
                    items = {}
                    product.config = json.dumps(items, cls=DjangoJSONEncoder)
                    product.save()
        if not isinstance(max_num, int):
            max_num = super(ProductAttributeInline, self).get_max_num(request, obj, **kwargs)
        return max_num


class FeatureProductInlineFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        parent = kwargs.get('instance')
        if 'initial' not in kwargs:
            kwargs['initial'] = []
        super(FeatureProductInlineFormSet, self).__init__(*args, **kwargs)
        # # This return initial [{'attribute' initial}, {..}, {..}]
        # self.initial = [{'feature_id': a} for a in parent.category.attributes.all()]
        # # Now we need to make a queryset to each field of each form inline
        # self.queryset = [{'value_option' .. }, { .. }]


class FeatureProductInline(NestedTabularInline):
    model = FeatureProduct
    # form = FeatureProductAdminForm
    # formset = FeatureProductInlineFormSet
    _parent_instance = None
    verbose_name = "Features In The Product"
    verbose_name_plural = "Features Of Product"
    extra = 1

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name not in ['attr_name', 'price', 'quantity']:  # Override the position widget to be a HiddenInput
            kwargs['widget'] = forms.HiddenInput()
        formfield = super(FeatureProductInline, self).formfield_for_dbfield(db_field, request, **kwargs)
        return formfield

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(FeatureProductInline, self).get_formset(request, obj, **kwargs)
        formset.request = request

        def formfield_callback(field, **kwargs):
            formfield = field.formfield(**kwargs)
            if field.name == 'feature_id':
                formfield.queryset = FeatureProduct.objects.filter(product_id=self._parent_instance)
            return formfield

        if self._parent_instance is not None:
            kwargs['formfield_callback'] = formfield_callback

        FeatureProductInline.form = type('FeatureProductAdminForm', (FeatureProductAdminForm,), {})
        return formset

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            extra = FeatureProduct.objects.filter(product_id=obj.product_id).count()
        else:
            _extra = super(FeatureProductInline, self).get_extra(request, obj, **kwargs)
        return 0 if obj and isinstance(extra, int) else _extra

    def get_max_num(self, request, obj=None, **kwargs):
        max_num = super(FeatureProductInline, self).get_max_num(request, obj, **kwargs)
        if obj:
            max_num = Feature.objects.all().count()
        return max_num


# https://www.thetopsites.net/article/52362929.shtml
@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    fieldsets = None
    form = ProductAdminForm

    inlines = [FeatureProductInline, ProductAttributeInline]  # add dyanmic in get_inline_instances
    list_display = (
        'thumbnail', 'name', 'quantity', 'unity', 'price', 'feature_count', 'attribute_count', 'show_set_url')
    list_filter = ('unity', 'active')
    search_fields = ('name', 'description_short', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('active', 'date_add')
    list_per_page = 10
    readonly_fields = ['config', ]

    fields = (
        ('manufacturer_id', 'category_default_id',),
        ('quantity', 'price', 'unity',),
        ('condition', 'show_price', 'file'),
        'name',
        'description_short',
        'description',
        'config'
    )

    class Media:
        js = ('/static/js/inline_handlers.js',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        product = kwargs.pop('obj', None)
        formfield = super(ProductAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "pro_attribute_id" and product:
            formfield.queryset = ProductAttribute.objects.filter(product_id=product)
        if db_field.name == "feature_id" and product:
            formfield.queryset = FeatureProduct.objects.filter(product_id=product)
        return formfield

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        product = kwargs.pop('obj', None)
        if db_field.name == "attributes" and product:
            kwargs['queryset'] = ProductAttributeGroup.objects.filter(product_id=product)
        return super(ProductAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(ProductAdmin, self).get_form(request, obj, **kwargs)

    def get_formsets(self, request, obj=None, *args, **kwargs):
        for inline in self.inline_instances:
            inline._parent_instance = obj
            yield inline.get_formset(request, obj)

    # If you wanted to manipulate the inline forms, to make one of the fields read-only:
    # https://www.programcreek.com/python/example/94429/django.contrib.admin.helpers.InlineAdminFormSet
    # https://stackoverflow.com/questions/5619120/readonly-for-existing-items-only-in-django-admin-inline
    # https://stackoverflow.com/questions/53257212/django-inline-how-to-get-inline-properties-in-change-view-django
    # def get_inline_formsets(self, request, formsets, inline_instances, obj=None):

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide/show market-specific inlines based on market name
            if obj and inline.__class__.__name__ in obj.extra_fields_by_attributes():
                yield inline.get_formset(request, obj), inline
        return super().get_formsets_with_inlines(request, obj)

    # https://stackoverflow.com/questions/5569091/django-admin-add-inlines-dynamically/5617361
    # https://stackoverflow.com/questions/5569091/django-admin-add-inlines-dynamically
    def get_inline_instances(self, request, obj=None):
        _inlines = self.inlines
        inline_instances = []
        # custom_inline = ProductAttributeInline(self.model, self.admin_site)
        # inline_instances.append(custom_inline)
        for inline_class in _inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    @mark_safe
    def show_set_url(self, obj):
        return '<a href="#">Set</a>'  # render depends on other fields

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        save_photo(request, obj)

    def save_formset(self, request, form, formset, change):
        flag = super(ProductAdmin, self).save_formset(request, form, formset, change)
        # parent_form = form
        try:
            instances = formset.save(commit=False)
            for instance in instances:
                # *** Start Coding for Custom Needs ***
                # *** End Coding for Custom Needs ***
                instance.save(commit=False)
            flag = flag and formset.save_m2m()
        except (ValueError, TypeError, IndexError, ObjectDoesNotExist):
            flag = False
        # parent = form.instance.save()  # form.instance is the parent
        # childes = formset.save()  # this will save the children
        if flag:
            form.instance.save()  # form.instance is the parent
            formset.save()  # this will save the children

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            attcount=Count("productattribute", distinct=True),
            featurecount=Count("featureproduct", distinct=True)
        )
        return queryset

    @mark_safe
    def feature_count(self, obj):
        instObjs = FeatureProduct.objects.filter(product_id=obj.product_id)
        value_of_alts = "{} values in [ ".format(str(obj.featurecount))
        i = 0
        for instObj in instObjs:
            if i == len(instObjs) - 1:
                value_of_alts += instObj.feature_value_id.value
            else:
                value_of_alts += instObj.feature_value_id.value + ", "
            i += 1
        value_of_alts += " ]"
        return value_of_alts

    feature_count.short_description = "Total Features"

    @mark_safe
    def attribute_count(self, obj):
        instObjs = ProductAttributeGroup.objects.filter(product_id=obj.product_id)
        value_of_alts = "{} values in [ ".format(str(obj.attcount))
        i = 0
        for instObj in instObjs:
            if i == len(instObjs) - 1:
                value_of_alts += instObj.attribute_id.name
            else:
                value_of_alts += instObj.attribute_id.name + ", "
            i += 1
        value_of_alts += " ]"
        return value_of_alts

    attribute_count.short_description = "Total Attributes"

    @mark_safe
    def thumbnail(self, obj):
        return preview(self, obj)

    thumbnail.allow_tags = True


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    form = ProductAttributeAdminForm
    list_display = (
        'thumbnail', 'attr_name', 'product_name', 'quantity', 'price', 'attributes_combination', 'features_collect',
        'upload_actions')
    list_filter = ('quantity', 'price', 'product_id')
    search_fields = ('attr_name', 'product_name', 'price')
    ordering = ('product_id', 'attr_name', 'date_add')
    list_per_page = 30
    readonly_fields = ['product_id', "headshot_image", "slider"]
    fields = (
        ('attr_name', 'price', 'quantity'),
        ('combination', 'product_id'),
        ('file', 'file1', 'file2', 'file3', 'file4', 'file5'),
        ("headshot_image", "slider"),
    )
    # actions = ['new_action', ]
    actions = ['delete_model']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    def delete_model(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    @mark_safe
    def headshot_image(self, obj):
        return format_html(thumbnail(obj, 'mid'))

    headshot_image.short_description = 'Headshot Image'
    headshot_image.allow_tags = True

    @mark_safe
    def slider(self, obj):
        return format_html(slider(obj, 'mid'))

    slider.short_description = 'Slider'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/upload/', self.admin_site.admin_view(self.upload_images), name='pro_attr_upload'),
        ]
        return custom_urls + urls

    @mark_safe
    def upload_actions(self, obj):
        return '<a class="button" href="{}">Uploads</a>'.format(
            reverse('admin:pro_attr_upload', args=(obj.pro_attribute_id,)))

    upload_actions.short_description = 'Mores Actions'
    upload_actions.allow_tags = True

    def upload_images(self, request, pk, *args, **kwargs):
        return self.process_action(request=request, pk=pk, action_form=ProductAttributeAdminForm,
                                   action_title='Uploads')

    def process_action(self, request, pk, action_form, action_title):
        pro_att = ProductAttribute.objects.get(pk=pk)
        if request.method != 'POST':
            form = action_form()
        else:
            form = action_form(request.POST)
        if form.is_valid():
            try:
                form.save(pro_att, request.user)
            except (ValueError, IndexError, KeyError):
                # If save() raised, the form will a have a non
                # field error containing an informative message.
                pass
        # else:
        # self.message_user(request, 'Success')
        # url = reverse('admin:index')
        # return HttpResponseRedirect(url)
        context = self.admin_site.each_context(request)
        context['form'] = form
        context['pro_att'] = pro_att
        context['title'] = action_title
        return TemplateResponse(request, 'admin/cus_form.html', context, )

    def new_action(self, request, queryset):
        pass
        # queryset.update(order_status=Order.CANCELLED)

    upload_images.short_description = "Uploads & Add Info"

    # This will help you to disbale add functionality
    def has_add_permission(self, request):
        return False

    # This will help you to disable delete functionaliyt
    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        save_photo(request, obj)

    @mark_safe
    def product_name(self, obj):
        return obj.product_id.name

    @mark_safe
    def features_collect(self, obj):
        instObjs = FeatureProduct.objects.filter(product_id=obj.product_id.product_id)
        value_of_alts = "[ "
        i = 0
        for instObj in instObjs:
            if i == len(instObjs) - 1:
                value_of_alts += instObj.feature_value_id.value
            else:
                value_of_alts += instObj.feature_value_id.value + ", "
            i += 1
        value_of_alts += " ]"
        return value_of_alts

    @mark_safe
    def attributes_combination(self, obj):
        instObjs = ProductAttributeCombination.objects.filter(pro_attribute_id=obj)
        value_of_alts = "[ "
        i = 0
        for instObj in instObjs:
            if i == len(instObjs) - 1:
                value_of_alts += instObj.attribute_id.name
            else:
                value_of_alts += instObj.attribute_id.name + ", "
            i += 1
        value_of_alts += " ]"
        return value_of_alts

    @mark_safe
    def thumbnail(self, obj):
        return preview(self, obj)

    thumbnail.allow_tags = True


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    form = ManufacturerAdminForm
    list_display = ('thumbnail', 'name', 'description_short', 'active', 'date_add')
    list_filter = ('active', 'date_add')
    search_fields = ('name', 'description_short', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('active', 'date_add')
    list_per_page = 5
    actions = ['delete_model']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    def delete_model(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    @mark_safe
    def thumbnail(self, obj):
        return preview(self, obj)

    thumbnail.allow_tags = True

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        save_photo(request, obj)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('thumbnail', 'title', 'short_content', 'status', 'date_add', "comment_count")
    list_filter = ('status', 'date_add')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('status', 'date_add')
    list_per_page = 5
    # exclude = ['user_add_id', 'user_upd_id',]
    actions = ['delete_model']
    fields = (
        ('category_id', 'status'),
        'title',
        'content',
        ('tags', 'file1', 'file', 'file2'),
    )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    def delete_model(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'user_add', None) is None:
            obj.user_add = request.user
        obj.user_upd = request.user
        obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)
        proccess_photo(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            commentcount=Count("comment", distinct=True)
        )
        return queryset

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    @mark_safe
    def thumbnail(self, obj):
        return preview(self, obj)

    thumbnail.allow_tags = True

    @mark_safe
    def comment_count(self, obj):
        # return '<img src="%s" height="24"/>' % thumb
        return str(obj.commentcount) + ' comments'

    comment_count.allow_tags = True

    @mark_safe
    def short_content(self, obj):
        return truncatechars(obj.content, 128)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ("thumbnail", "name", "short_description", "post_count")
    list_filter = ('active', 'date_add')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('active', 'date_add')
    list_per_page = 5

    actions = ['delete_model']

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    def delete_model(self, request, queryset):
        for obj in queryset:
            del_photo(request, obj)
        queryset.delete()

    def render_change_form(self, request, context, *args, **kwargs):
        """We need to update the context to show the button."""
        context.update({'show_save_and_copy': True})
        return super().render_change_form(request, context, *args, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            postcount=Count("post", distinct=True)
        )
        return queryset

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        save_photo(request, obj)

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    @mark_safe
    def thumbnail(self, obj):
        return preview(self, obj)

    thumbnail.allow_tags = True

    @staticmethod
    def short_description(obj):
        from django.utils.html import strip_tags
        return strip_tags(truncatechars(obj.description, 128))

    @mark_safe
    def post_count(self, obj):
        return str(obj.postcount) + ' posts'


# Show graphics
# https://www.neerajbyte.com/post/how-to-make-charts-in-django-admin-interface/
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_en', 'frequency')
    list_filter = ('name', 'name_en', 'frequency')
    save_as = True
    save_on_top = True
    change_list_template = 'admin/change_list_graph.html'

    class Media:
        js = ('/static/js/dynamic_inlines_with_sort.js',)
        css = {'all': ['/static/css/dynamic_inlines_with_sort.css'], }


@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    form = FeatureValueAdminForm
    list_display = ('name_of_feature', 'value', 'custom', 'value_count')
    list_filter = ('value', 'custom',)
    search_fields = ('value',)
    ordering = ('value', 'custom')
    list_per_page = 20

    class Media:
        js = (
            'js/exam_form.js',
        )

    @mark_safe
    def name_of_feature(self, obj):
        return obj.feature_id.name

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "feature_value_id":
            try:
                feature_value_id = request.resolver_match.args[0]
                kwargs["queryset"] = FeatureValue.objects.filter(
                    feature_value_id=feature_value_id).order_by('value')
            except IndexError:
                pass
        return super(FeatureValueAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.custom:
            form.instance.custom = form.cleaned_data['custom'] = 0
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            valuecount=Count("featureproduct", distinct=True)
        )
        return queryset

    @mark_safe
    def value_count(self, obj):
        return str(obj.valuecount) + ' has Products '


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    form = FeatureAdminForm
    list_display = ('name', 'position', 'value_count')
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name', 'position')
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            valuecount=Count("featurevalue", distinct=True)
        )
        return queryset

    @mark_safe
    def value_count(self, obj):
        return str(obj.valuecount) + ' Value Of Features '


@admin.register(FeatureProduct)
class FeatureProductAdmin(admin.ModelAdmin):
    form = FeatureProductAdminForm
    list_display = ('name_of_product', 'name_of_feature', 'value_of_feature')
    ordering = ('product_id', 'feature_id', 'feature_value_id')
    list_per_page = 20

    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            self.exclude = ('Feature', 'FeatureValue')
        else:
            self.exclude = ()
        return super(FeatureProductAdmin, self).get_form(request, obj=None, **kwargs)

    @mark_safe
    def name_of_product(self, obj):
        return obj.product_id.name

    @mark_safe
    def name_of_feature(self, obj):
        return obj.feature_id.name

    @mark_safe
    def value_of_feature(self, obj):
        if isinstance(obj.feature_value_id, FeatureValue):
            return obj.feature_value_id.value
        else:
            try:
                feature_value = FeatureValue.objects.get(feature_value_id=obj.feature_value_id)
                return feature_value.value
            except MultipleObjectsReturned or IntegrityError:
                return feature_value.value


@admin.register(Lookup)
class LookupAdmin(admin.ModelAdmin):
    form = LookupAdminForm
    list_display = ('name', 'code', 'type', 'position')
    list_filter = ('type',)
    search_fields = ('name', 'code', 'type')
    ordering = ('type', 'position')
    list_per_page = 20


class WardInline(NestedTabularInline):
    model = Ward
    extra = 1


class DistrictInline(NestedStackedInline):
    model = District
    inlines = [WardInline]
    extra = 1


@admin.register(City)
class CityAdmin(NestedModelAdmin):
    form = CityAdminForm
    inlines = [DistrictInline]
    list_display = ('name', 'date_add', 'total_districts', 'total_wards')
    list_filter = ('iso_code',)
    search_fields = ('name',)
    ordering = ('name', 'date_add')
    list_per_page = 5

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            districtcount=Count("district", distinct=True)
        )
        return queryset

    @mark_safe
    def total_districts(self, obj):
        return str(obj.districtcount) + ' Districts'

    total_districts.short_description = "Total Districts of City"

    @mark_safe
    def total_wards(self, obj):
        districts = District.objects.filter(city_id=obj.pk)
        total = 0
        for district in districts:
            wards = Ward.objects.filter(district_id=district.pk)
            total += districts.count()
        return str(districts.count()) + ' Districts has total %d Wards ' % total

    total_wards.short_description = "Total Wards of Districts"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


def get_static(path):
    if settings.DEBUG:
        return find(path)
    else:
        return static(path)


# https://www.google.com/search?client=ubuntu&channel=fs&q=Handling+tabular+data+loading+and+validation+in+djangoadmin&ie=utf-8&oe=utf-8
# https://gist.github.com/klodi/1559767#file-dynamic_inlines_with_sort-css
# https://www.google.com/search?client=ubuntu&channel=fs&q=using+admin.TabularInline+in+django+admin&ie=utf-8&oe=utf-8
# https://stackoverflow.com/questions/33748059/add-inline-model-to-django-admin-site
# https://stackoverflow.com/questions/5249186/django-admin-tabularinline-is-there-a-good-way-of-adding-a-custom-html-column


def link_image(obj):
    full_url = mark_safe('<img	src="{url}"	width="{width}"	height={height}	/>'.format(url=obj.headshot.url,
                                                                                                  width=obj.headshot.width,
                                                                                                  height=obj.headshot.height))
    return full_url


def combinations(self, obj):
    return ''


def preview(self, obj, typ='sm'):
    real = settings.MEDIA_ROOT + '/' + obj.CONST_TYPE + '/'
    path = settings.MEDIA_URL + '/' + obj.CONST_TYPE + '/'
    found = False
    thumb = ""
    for ext in IMG_EXT_WITH_DOT:
        thumb = real + str(obj.pk) + ext
        if os.path.exists(thumb):
            thumb = str(obj.pk) + ext
            found = True
            break
    if found:
        thumb = path + thumb
    else:
        thumb = settings.MEDIA_URL + '/' + "noimage.jpg"
    return '<img src="%s" height="24"/>' % thumb


class CategoryFilter(SimpleListFilter):
    title = 'name'  # or use _('category') for translated title
    parameter_name = 'name'

    def lookups(self, request, category_admin):
        categories = set([c.category for c in category_admin.model.objects.all()])
        return [(c.category_id, c.name) for c in categories] + []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name__id__exact=self.value())


@mark_safe
def get_picture_preview(obj):
    if obj.pk:  # if object has already been saved and has a primary key, show picture preview
        return """<a href="{src}" target="_blank"><img src="{src}" alt="{title}" style="max-width: 200px; max-height: 200px;" /></a>""".format(
            src=obj.picture.url,
            title=obj.title,
        )
    return _("(choose a picture and save and continue editing to see the preview)")


get_picture_preview.allow_tags = True
get_picture_preview.short_description = "Picture Preview"


# read-only user filter class for ModelAdmin
# https://stackoverflow.com/questions/8265328/readonly-models-in-django-admin-interface
class ReadOnlyAdmin(admin.ModelAdmin):
    actions = None  # actions = None: avoids showing the dropdown with the "Delete selected ..." option
    list_display_links = None  # list_display_links = None: avoids clicking in columns to edit that object
    readonly_fields = []

    # more stuff here

    def __init__(self, *args, **kwargs):
        # keep initial readonly_fields defined in subclass
        self._init_readonly_fields = self.readonly_fields
        # keep also inline readonly_fields
        for inline in self.inlines:
            inline._init_readonly_fields = inline.readonly_fields
        super().__init__(*args, **kwargs)

    # has_add_permission() returning False avoids creating new objects for that model
    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # customize change_view to disable edition to readonly_users
    def change_view(self, request, object_id, form_url='', extra_context=None):
        context = extra_context or {}
        # find whether it is readonly or not
        if request.user.is_readonly():
            # put all fields in readonly_field list
            self.readonly_fields = [field.name for field in self.model._meta.get_fields() if not field.auto_created]
            # readonly mode fer all inlines
            for inline in self.inlines:
                inline.readonly_fields = [field.name for field in inline.model._meta.get_fields() if
                                          not field.auto_created]
            # remove edition buttons
            self.save_on_top = False
            context['show_save'] = False
            context['show_save_and_continue'] = False
        else:
            # if not readonly user, reset initial readonly_fields
            self.readonly_fields = self._init_readonly_fields
            # same for inlines
            for inline in self.inlines:
                inline.readonly_fields = self._init_readonly_fields
        return super().change_view(request, object_id, form_url, context)

    def save_model(self, request, obj, form, change):
        # disable saving model for readonly users
        # just in case we have a malicious user...
        if request.user.is_readonly():
            # si és usuari readonly no guardem canvis
            return False
        # if not readonly user, save model
        return super().save_model(request, obj, form, change)


class MyModelAdmin(ReadOnlyAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(MyModelAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class ReadOnlyTabularInline(admin.TabularInline):
    extra = 0
    can_delete = False
    editable_fields = []
    readonly_fields = []
    exclude = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + [field.name for field in self.model._meta.fields
                                             if field.name not in self.editable_fields and
                                             field.name not in self.exclude]

    def has_add_permission(self, request):
        return False


class MyInline(ReadOnlyTabularInline):
    pass
