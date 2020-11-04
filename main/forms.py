import os
import pdb

from captcha.fields import CaptchaField
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Div
from .const import CityModelChoiceField, DistrictModelChoiceField, WardModelChoiceField, MAX_SIZE_UPLOADED, \
    SERVICE_CHOICES
from .models import Comment, Address, District, Ward, City, OrderPayment, OrderInvoice, Post, Contact


class OrderInvoiceForm(forms.ModelForm):
    class Meta:
        model = OrderInvoice
        fields = ["amount", "note"]


class OrderPaymentForm(forms.ModelForm):
    data_payment = forms.CharField(widget=CKEditorUploadingWidget(config_name='basic'))

    class Meta:
        model = OrderPayment
        fields = ["order_reference", "amount", "payment_method", "data_payment"]

    file1 = forms.FileField(required=False, label='Upload File1')
    file2 = forms.FileField(required=False, label='Upload File2')
    file3 = forms.FileField(required=False, label='Upload File3')
    file4 = forms.FileField(required=False, label='Upload File4')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(OrderPaymentForm, self).__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance is not None:
            if isinstance(instance, OrderPayment) and isinstance(instance.pk, int) and instance.CONST_TYPE is not None:
                folder = "{}/{}".format(instance.CONST_TYPE, instance.pk)
                path = settings.MEDIA_ROOT + '/' + folder
                try:
                    os.makedirs(path, exist_ok=True)
                except (OSError, SystemError):
                    pass
                cur_len = sum(len(files) for _, _, files in os.walk(path))
                if cur_len >= int(MAX_SIZE_UPLOADED):
                    for i in range(1, MAX_SIZE_UPLOADED + 1):
                        field = "file{}".format(i)
                        self.fields[field].widget = forms.HiddenInput()
                else:
                    remain = int(MAX_SIZE_UPLOADED) if cur_len is None or cur_len <= 0 else int(
                        MAX_SIZE_UPLOADED) - cur_len
                    remain = min(remain, MAX_SIZE_UPLOADED)
                    for i in range(remain + 1, MAX_SIZE_UPLOADED + 1):
                        field = "file{}".format(i)
                        self.fields[field].widget = forms.HiddenInput()


class AddressForm(forms.ModelForm):
    city_id = CityModelChoiceField(queryset=City.objects.all())
    district_id = DistrictModelChoiceField(queryset=District.objects.filter(city_id=None))
    ward_id = WardModelChoiceField(queryset=Ward.objects.filter(district_id=None))

    class Meta:
        model = Address
        fields = ["address", "mobile", "city_id", "district_id", "ward_id"]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['city_id'].queryset = City.objects.all()

        instance = kwargs.get("instance")
        if instance is not None:
            self.initial['city_id'] = instance.city_id

            self.fields['district_id'].queryset = District.objects.filter(
                city_id=instance.city_id)
            self.initial['district_id'] = instance.district_id

            self.fields['ward_id'].queryset = Ward.objects.filter(
                district_id=instance.district_id)
            self.initial['ward_id'] = instance.ward_id
        else:
            self.fields['district_id'].queryset = District.objects.filter(city_id=None)
            self.fields['ward_id'].queryset = Ward.objects.filter(district_id=None)
        # Get did queryset for the selected fid
        if 'city_id' in self.data:
            try:
                city_id = int(self.data.get('city_id'))
                self.fields['district_id'].queryset = District.objects.filter(city_id=city_id).order_by('-name')
                if 'district_id' in self.data:
                    district_id = int(self.data.get('district_id'))
                    self.fields['ward_id'].queryset = Ward.objects.filter(district_id=district_id).order_by('-name')
            except (ObjectDoesNotExist, IndexError, ValueError, ValueError, TypeError):
                pass


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content', 'post_id', 'owner', 'captcha')

    readonly_fields = ['post_id', ]
    content = forms.CharField(widget=CKEditorUploadingWidget(config_name='tiny'))
    captcha = CaptchaField()

    # content = SanitizedTextField(widget=CKEditorUploadingWidget(config_name='tiny'), max_length=255,
    #                              allowed_tags=['a', 'p', 'img'],
    #                              allowed_attributes=['href', 'src'], strip=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        self.post = kwargs.pop('post', None)
        super(CommentForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)

        if instance and self.post:
            self.fields['post_id'].queryset = Post.objects.filter(pk=self.post.pk)
            self.fields['post_id'].required = False
            self.fields['post_id'].widget.attrs['disabled'] = 'disabled'
            self.initial['post_id'] = self.post
        else:
            self.fields['post_id'].queryset = Post.objects.filter(pk=None)
        if instance and self.user:
            self.fields['owner'].queryset = User.objects.filter(pk=self.user.id)
            self.fields['owner'].required = False
            self.fields['owner'].widget.attrs['disabled'] = 'disabled'
            self.initial['owner'] = self.user
        else:
            self.fields['owner'].queryset = User.objects.filter(pk=None)

    def clean_post_id(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.post_id:
            self.initial['post_id'] = instance.post_id
            return instance.post_id
        else:
            self.initial['post_id'] = self.post
            return self.post

    def clean_owner(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.owner:
            self.initial['owner'] = instance.owner
            return instance.owner
        else:
            self.initial['owner'] = self.user
            return self.user

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.owner = self.user
            obj.post_id = self.post
        super(CommentForm, self).save_model(request, obj, form, change)


class ContactForm(forms.Form):
    company = forms.CharField(label="Your company", max_length=100)
    name = forms.CharField(label="Your name", max_length=100, required=True)
    email = forms.CharField(label="Your email", max_length=100, required=True)
    mobile = forms.CharField(label="Your mobile", max_length=100, required=True)
    description = forms.CharField(widget=CKEditorUploadingWidget(config_name='tiny'), required=True)
    customer_service = forms.ChoiceField(choices=SERVICE_CHOICES)
    captcha = CaptchaField()

    class Meta:
        model = Contact
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        super(ContactForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if self.user and isinstance(self.user, User):
            self.fields['name'].required = False
            self.fields['name'].widget.attrs['disabled'] = 'disabled'
            self.initial['name'] = "{} {}".format(self.user.first_name, self.user.last_name)

            self.fields['email'].required = False
            self.fields['email'].widget.attrs['disabled'] = 'disabled'
            self.initial['email'] = "{}".format(self.user.email)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save person'))

    def clean_name(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.name:
            self.initial['name'] = instance.name
            return instance.name
        else:
            self.initial['name'] = "{} {}".format(self.user.first_name, self.user.last_name) if self.user else None
            return self.initial['name']

    def clean_email(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.email:
            self.initial['email'] = instance.email
            return instance.email
        else:
            self.initial['email'] = "{}".format(self.user.email) if self.user else None
            return self.initial['email']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.name = "{} {}".format(self.user.first_name, self.user.last_name)
            obj.email = self.user.email
        super(ContactForm, self).save_model(request, obj, form, change)

    def send_mail(self):
        message = "From: {0}\n{1}".format(
            self.cleaned_data["name"],
            self.cleaned_data["description"],
        )
        send_mail(
            "Site message",
            message,
            "site@booktime.domain",
            ["customerservice@booktime.domain"],
            fail_silently=False,
        )
