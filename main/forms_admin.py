from random import randint

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django_json_widget.widgets import JSONEditorWidget
from django_mysql.models import JSONField

from spa import utils
from .const import CatModelChoiceField, UnityModelChoiceField, FeatureModelChoiceField, \
    ProductModelChoiceField, FeatureValueModelChoiceField, GROUP_CHOICES, AttributeModelChoiceField, \
    AttributeGroupModelChoiceField, ProductAttributeModelChoiceField, CombineByMeModelChoiceField
from .models import Post, Category, CategoryProductAttribute, CategoryProduct, PostCategory, Product, \
    Manufacturer, Lookup, Feature, FeatureValue, FeatureProduct, City, District, Ward, ProductAttribute, \
    ProductAttributeTag, Customization, ProductAttributeCombination, AttributeGroup, Attribute, ProductAttributeGroup, \
    Address, Service


class ServiceAdminForm(forms.Form):
    class Meta:
        model = Service
        fields = '__all__'
        exclude = [Attribute, ProductAttribute]


class ProductAttributeCombinationForm(forms.Form):
    pro_attribute_id = ProductAttributeModelChoiceField(queryset=ProductAttribute.objects.all())
    attribute_id = AttributeModelChoiceField(queryset=Attribute.objects.all())

    class Meta:
        model = ProductAttributeCombination
        fields = '__all__'
        exclude = [Attribute, ProductAttribute]

    combination = forms.CharField(required=False, widget=forms.HiddenInput())


class ProductAttributeForm(forms.Form):
    name = forms.CharField(
        label='Attribute Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Attribute Name here'
        })
    )
    price = forms.CharField(
        label='Price',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Price here'
        })
    )

    def __init__(self, *args, **kwargs):
        super(ProductAttributeForm, self).__init__(*args, **kwargs)
        if self.instance is not None and isinstance(self.instance, ProductAttribute) and self.instance.pk:
            current_event = self.instance.event
            self.fields['combination'] = CombineByMeModelChoiceField()


class ProductAttributeGroupAdminForm(forms.ModelForm):
    product_id = ProductModelChoiceField(queryset=Product.objects.all())
    attr_group_id = AttributeGroupModelChoiceField(queryset=AttributeGroup.objects.all())
    attribute_id = AttributeModelChoiceField(queryset=Attribute.objects.all())

    class Meta:
        model = ProductAttributeGroup
        fields = '__all__'
        exclude = [Attribute, AttributeGroup, Product]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProductAttributeGroupAdminForm, self).__init__(*args, **kwargs)
        self.fields['attribute_id'].queryset = Attribute.objects.all()
        # self.fields['product_id'].queryset = Product.objects.all()
        instance = kwargs.get("instance")
        if instance is not None:
            self.fields['attribute_id'].queryset = Attribute.objects.filter(
                attr_group_id=instance.attr_group_id)
            self.initial['product_id'] = instance.product_id
            self.fields['product_id'].widget.attrs['disabled'] = 'disabled'
            self.fields['product_id'].widget.attrs['value'] = instance.product_id
            self.fields['product_id'].widget.attrs['readonly'] = True

        if hasattr(self, 'readonly'):
            for x in self.readonly:
                self.fields[x].widget.attrs['disabled'] = 'disabled'

        # add a "form-control" class to each form input for enabling bootstrap
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

    def is_valid(self):
        return super(ProductAttributeGroupAdminForm, self).is_valid()

    def save(self, *args, **kwargs):
        instance = kwargs.get("instance")
        if instance is not None and 'product_id' in self._errors:
            del self._errors['product_id']
        return super(ProductAttributeGroupAdminForm, self).save(*args, **kwargs)

    def clean_product_id(self):
        instance = getattr(self, 'instance', None)
        product_id = self.cleaned_data['product_id']
        if instance is not None:
            try:
                if 'product_id' in self._errors:
                    if isinstance(product_id, int):
                        self.initial['product_id'] = product_id
                    elif isinstance(self.data['product_id'], int):
                        product_id = self.initial['product_id'] = self.data['product_id']
                    else:
                        product_id = self.initial['product_id'] = instance.product_id
                        # remove the error
                    del self._errors['product_id']
            except (ValueError, IndexError, KeyError):
                raise ValidationError('product_id error in clean_product_id...')
        return product_id

    # https://stackoverflow.com/questions/12278753/clean-method-in-model-and-field-validation
    def clean(self):
        super(ProductAttributeGroupAdminForm, self).clean()  # if necessary
        instance = getattr(self, 'instance', None)
        if instance is not None:
            try:
                if 'product_id' in self._errors:
                    if isinstance(self.cleaned_data['product_id'], int):
                        self.initial['product_id'] = self.cleaned_data['product_id']
                    elif isinstance(self.data['product_id'], int):
                        self.initial['product_id'] = self.data['product_id']
                    else:
                        self.initial['product_id'] = instance.product_id
                    # remove the error
                    if isinstance(self.initial['product_id'], int):
                        raise forms.ValidationError("A Question must have an answer.")
            except (ValueError, IndexError, KeyError):
                del self._errors['product_id']
        return self.cleaned_data


class AttributeGroupAdminForm(forms.ModelForm):
    group_type = forms.ChoiceField(choices=GROUP_CHOICES)

    class Meta:
        model = AttributeGroup
        fields = '__all__'
        exclude = [Attribute, ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AttributeGroupAdminForm, self).__init__(*args, **kwargs)
        # if self.instance and self.instance.pk:
        #     self.fields['date_add'].widget = forms.HiddenInput()


class CityAdminForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'
        exclude = [District, Ward]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CityAdminForm, self).__init__(*args, **kwargs)
        # if self.instance and self.instance.pk:
        #     self.fields['date_add'].widget = forms.HiddenInput()

    def district_list(self, inst):
        url = u'../modelb/?modela__id__exact=%d' % inst.id
        return u'<a href="%s">Models B</a>' % url

    district_list.allow_tags = True
    district_list.short_description = u'Models Ware'


class LookupAdminForm(forms.ModelForm):
    class Meta:
        model = Lookup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LookupAdminForm, self).__init__(*args, **kwargs)


class ManufacturerAdminForm(forms.ModelForm):
    slug = forms.CharField(widget=forms.HiddenInput(), initial=utils.generate_slug())
    description_short = forms.CharField(widget=CKEditorUploadingWidget(config_name='tiny'))
    description = forms.CharField(widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = Manufacturer
        fields = '__all__'

    file = forms.FileField(required=False, label='Upload an image')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ManufacturerAdminForm, self).__init__(*args, **kwargs)


class PostAdminForm(forms.ModelForm):
    readonly_fields = ('user_add_id', 'user_upd_id', 'slug')
    category_id = CatModelChoiceField(queryset=Category.objects.all())
    user_upd_id = forms.CharField(required=False, widget=forms.HiddenInput())
    slug = forms.CharField(widget=forms.HiddenInput(), initial=utils.generate_slug())
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = Post
        exclude = [Category]
        fields = '__all__'

    file = forms.FileField(required=False, label='Upload an image')
    file1 = forms.FileField(required=False, label='Upload Height image')
    file2 = forms.FileField(required=False, label='Upload Width image')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PostAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance is not None:
            try:
                if instance.title is not None:
                    field_name = 'slug'
                    self.initial[field_name] = slugify(instance.title)
            except (ValueError, IndexError, KeyError, TypeError):
                pass

    def clean_slug(self):
        instance = getattr(self, 'instance', None)
        slug = slugify(self.cleaned_data['title'])
        if instance is not None:
            try:
                if 'title' not in self._errors:
                    slug = self.initial['slug'] = slugify(self.data['title'])
            except (ValueError, IndexError, KeyError):
                pass
        if 'slug' in self._errors:
            del self._errors['slug']
        return slug

    def clean(self):
        cleaned_data = super(PostAdminForm, self).clean()  # if necessary
        if 'title' in cleaned_data:
            self.slug = slugify(cleaned_data['title'])
        instance = getattr(self, 'instance', None)
        if instance is not None:
            try:
                self.initial['slug'] = slugify(instance.title)
            except (ValueError, IndexError, KeyError, TypeError):
                pass
        if 'slug' in self._errors:
            del self._errors['slug']
        return self.cleaned_data


class CategoryAdminForm(forms.ModelForm):
    readonly_fields = ('slug',)
    slug = forms.CharField(widget=forms.HiddenInput(), initial=utils.generate_slug())
    description = forms.CharField(widget=CKEditorUploadingWidget(config_name='default'))

    class Meta:
        model = Category
        fields = '__all__'
        exclude = [PostCategory, CategoryProductAttribute, CategoryProduct]

    file = forms.FileField(required=False, label='Upload an image')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CategoryAdminForm, self).__init__(*args, **kwargs)

    def clean(self):
        from django.utils.html import strip_tags
        cleaned_data = super(CategoryAdminForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data.get('name'))
        return cleaned_data


class ProductAdminForm(forms.ModelForm):
    readonly_fields = ('slug',)
    slug = forms.CharField(widget=forms.HiddenInput(), initial=utils.generate_slug())
    description_short = forms.CharField(widget=CKEditorUploadingWidget(config_name='tiny'))
    description = forms.CharField(widget=CKEditorUploadingWidget(config_name='default'))
    unity = UnityModelChoiceField(queryset=Lookup.objects.all().filter(type='DonVi'))
    price = forms.DecimalField(max_digits=20, decimal_places=3)
    formfield_overrides = {
        # JSONField: {'widget': JSONEditorWidget(mode='code', height='250px', width='100%')},
        JSONField: {'widget': JSONEditorWidget(mode='code', height='250px', width='100%')},
    }

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'config': JSONEditorWidget
        }
        exclude = [FeatureProduct]

    file = forms.FileField(required=False, label='Upload an image')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        choices = [(lookup.code, lookup.name) for lookup in Lookup.objects.all().filter(type='DonVi')]
        self.fields['unity'] = forms.ChoiceField(choices=choices)
        if instance is not None:
            try:
                if instance.name is not None:
                    field_name = 'slug'
                    self.initial[field_name] = slugify(instance.name)
            except (ValueError, IndexError, KeyError, TypeError):
                pass

    def clean_slug(self):
        instance = getattr(self, 'instance', None)
        slug = slugify(self.cleaned_data['name'])
        if instance is not None:
            try:
                if 'name' not in self._errors:
                    slug = self.initial['slug'] = slugify(self.data['name'])
            except (ValueError, IndexError, KeyError):
                pass
        if 'slug' in self._errors:
            del self._errors['slug']
        return slug

    def clean(self):
        cleaned_data = super(ProductAdminForm, self).clean()  # if necessary
        if 'name' in cleaned_data:
            self.slug = slugify(cleaned_data['name'])
        instance = getattr(self, 'instance', None)
        if instance is not None:
            try:
                self.initial['slug'] = slugify(instance.name)
            except (ValueError, IndexError, KeyError, TypeError):
                pass
        if 'slug' in self._errors:
            del self._errors['slug']
        return self.cleaned_data


class ProductAttributeInlineForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = '__all__'
        exclude = [ProductAttributeTag, Customization, ProductAttributeCombination]

    file = forms.FileField(required=False, label='Upload an image')
    file1 = forms.FileField(required=False, label='Alt Cover image')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProductAttributeInlineForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance is not None:
            try:
                attributes = ProductAttributeCombination.objects.filter(pro_attribute_id=instance)
                field_value = ""
                for attribute in attributes:
                    field_value += "{}:{}, ".format(attribute.attribute_id.pk, attribute.attribute_id.name)
                if attributes is not None:
                    new_fields = {}
                    # field = forms.CharField(required=False,)
                    field = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
                    field_name = 'combination'
                    new_fields[field_name] = field
                    self.initial[field_name] = field_value
                    self.fields[field_name].widget.attrs['disabled'] = 'disabled'
                    self.fields.update(new_fields)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        else:
            self.initial['quantity'] = 10
            self.initial['price'] = '{}0000'.format(randint(1, 100))


class ProductAttributeAdminForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = '__all__'
        exclude = [ProductAttributeTag, Customization, ProductAttributeCombination]

    file = forms.FileField(required=False, label='Cover image')
    file1 = forms.FileField(required=False, label='Alt Cover image')

    file2 = forms.FileField(required=False, label='Slider an image 1')
    file3 = forms.FileField(required=False, label='Slider an image 2')
    file4 = forms.FileField(required=False, label='Slider an image 3')
    file5 = forms.FileField(required=False, label='Slider an image 4')
    combination = forms.CharField(required=False, )

    def save(self, commit=True):
        combination = self.cleaned_data.get('combination', None)
        # Get the form instance so I can write to its fields
        instance = super(ProductAttributeAdminForm, self).save(commit=commit)

        # this writes the processed data to the description field
        self.processData(combination)

        if commit:
            instance.save()

        return instance

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProductAttributeAdminForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance is not None:
            try:
                attributes = ProductAttributeCombination.objects.filter(pro_attribute_id=instance)
                field_value = ""
                for attribute in attributes:
                    field_value += "{}:{}, ".format(attribute.attribute_id.pk, attribute.attribute_id.name)
                if attributes is not None:
                    self.initial['combination'] = field_value
                    self.fields['combination'].widget.attrs['disabled'] = 'disabled'
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset

    def processData(self, value=None):
        if isinstance(value, str):
            print(value)
        elif isinstance(value, int):
            print(value)
        else:
            print(value)


class FeatureAdminForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = '__all__'
        exclude = [FeatureValue, FeatureProduct]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FeatureAdminForm, self).__init__(*args, **kwargs)


class FeatureValueAdminForm(forms.ModelForm):
    feature_id = FeatureModelChoiceField(queryset=Feature.objects.all())

    class Meta:
        model = FeatureValue
        fields = '__all__'
        exclude = [Feature, FeatureProduct]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FeatureValueAdminForm, self).__init__(*args, **kwargs)
        # choices = [(feature.pk, feature.name) for feature in Feature.objects.all()]
        # self.fields['feature_id'] = forms.ChoiceField(choices=choices)


class FeatureProductAdminForm(forms.ModelForm):
    feature_id = FeatureModelChoiceField(queryset=Feature.objects.all())
    product_id = ProductModelChoiceField(queryset=Product.objects.all())
    feature_value_id = FeatureValueModelChoiceField(queryset=FeatureValue.objects.all())

    class Meta:
        model = FeatureProduct
        fields = '__all__'
        exclude = [Feature, Product, FeatureValue]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FeatureProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['feature_value_id'].queryset = FeatureValue.objects.all()
        instance = kwargs.get("instance")
        if instance is not None:
            self.fields['feature_value_id'].queryset = FeatureValue.objects.all().filter(
                feature_id=kwargs['instance'].feature_id)
        for name in self.fields.keys():
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
            })

    def save(self, commit=True):
        # Get the form instance so I can write to its fields
        instance = super(FeatureProductAdminForm, self).save(commit=commit)
        if commit:
            instance.save()
        return instance


class AddressInlineForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
        exclude = [City, Ward, District]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddressInlineForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance is not None:
            print(instance)
        else:
            self.fields['city_id'].queryset = City.objects.all()
            self.fields['ward_id'].queryset = Ward.objects.all()[:10]
            self.fields['district_id'].queryset = District.objects.all()[:10]
