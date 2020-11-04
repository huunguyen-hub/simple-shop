# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import ast
from decimal import Decimal

from django.contrib.auth.models import User
from django.core import serializers
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify

from main.const import STATUS_CHOICES2, ACTIVE_CHOICES, STATUS_CHOICES3, SHOW_CHOICES, COND_CHOICES, ROLE_CHOICES, \
    VERIFY_CHOICES, MA_STATUS_CHOICES, GENDER_CHOICES, METHOD_PAYMENT_CHOICES, SIGN_CHOICES, SERVICE_CHOICES
from spa.utils import to_python, is_json, almost_lt, generate_slug, del_photo, proccessConfig


# from django.contrib.auth import get_user_model
# User = get_user_model()


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(auto_now=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.SmallIntegerField(choices=ACTIVE_CHOICES, default=1)
    is_active = models.SmallIntegerField(choices=ACTIVE_CHOICES, default=1)
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Actor(models.Model):
    actor_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=245, blank=True, null=True)
    workingtime = models.TextField(blank=True, null=True)  # This field type is a guess.
    rating = models.IntegerField(blank=True, null=True)
    price_extra = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    available_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'actor'


class Address(models.Model):
    address_id = models.AutoField(primary_key=True)
    city_id = models.ForeignKey('City', models.DO_NOTHING, db_column='city_id')
    district_id = models.ForeignKey('District', models.DO_NOTHING, db_column='district_id', blank=True, null=True)
    ward_id = models.ForeignKey('Ward', models.DO_NOTHING, db_column='ward_id', blank=True, null=True)
    address = models.CharField(max_length=128)
    mobile = models.CharField(max_length=16)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'address'


class AnswerCustomer(models.Model):
    ans_customer_id = models.PositiveIntegerField(primary_key=True)
    answer_id = models.ForeignKey('Comment', models.DO_NOTHING, db_column='answer_id')
    user_id = models.PositiveIntegerField()
    ex_info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'answer_customer'


class Attribute(models.Model):
    attribute_id = models.AutoField(primary_key=True)
    attr_group_id = models.ForeignKey('AttributeGroup', models.DO_NOTHING, db_column='attr_group_id')
    color = models.CharField(max_length=32, blank=True, null=True)
    name = models.CharField(max_length=45)
    position = models.PositiveIntegerField()

    # product_attributes = models.ManyToManyField('ProductAttribute', through='ProductAttributeCombination')

    class Meta:
        managed = False
        db_table = 'attribute'


class AttributeGroup(models.Model):
    attr_group_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=45)
    public_name = models.CharField(unique=True, max_length=45)
    group_type = models.CharField(max_length=6)
    position = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'attribute_group'


class Behavior(models.Model):
    behavior_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    type = models.CharField(max_length=7, blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'behavior'


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    address = models.OneToOneField(Address, models.DO_NOTHING, db_column='address_id', unique=True, null=True,
                                   blank=True)
    # Relations owner: in database need a field owner_id ??? cau hoi rat lon o day????
    owner = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    total_paid = models.DecimalField(max_digits=20, decimal_places=3)
    total_wrapping = models.DecimalField(max_digits=20, decimal_places=3)
    total_paid_real = models.DecimalField(max_digits=20, decimal_places=3)
    status = models.PositiveIntegerField(default=0)

    # objects = managers.CartManager()
    objects = models.Manager()  # The default manager.

    # Custom Properties
    @property
    def username(self):
        return self.owner.username

    class Meta:
        managed = False
        db_table = 'cart'
        ordering = ['-date_add']

    def __str__(self):
        return self.owner.username

    def __unicode__(self):
        return self.owner.username


class CartItem(models.Model):
    cart_id = models.OneToOneField(Cart, models.DO_NOTHING, db_column='cart_id')
    find_item_id = models.CharField(max_length=128, primary_key=True)
    class_of_item = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unity = models.CharField(max_length=45, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    original_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cart_item'
        unique_together = (('cart_id', 'find_item_id'),)
        ordering = ['-find_item_id']

    def save(self, *args, **kwargs):
        if to_python(self.class_of_item):
            try:
                _item = next(serializers.deserialize("json", self.class_of_item)).object
                if isinstance(_item, ProductAttribute):
                    self.price = _item.price
                    self.total_price = Decimal(_item.price) * self.quantity
            except:
                self.total_price = Decimal(self.price) * self.quantity
            finally:
                if almost_lt(self.total_price, 0.00, 2):
                    print("Something Wrong in save() CartItem {}".format(self.total_price))
        super(CartItem, self).save(*args, **kwargs)


class CategoryProduct(models.Model):
    auto_id = models.AutoField(primary_key=True)
    category_id = models.ForeignKey('Category', models.DO_NOTHING, db_column='category_id')
    product_id = models.ForeignKey('Product', models.DO_NOTHING, db_column='product_id')
    position = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'category_product'
        unique_together = (('category_id', 'product_id'),)


class CategoryProductAttribute(models.Model):
    auto_id = models.AutoField(primary_key=True)
    category_id = models.ForeignKey('Category', models.DO_NOTHING, db_column='category_id')
    product_id = models.ForeignKey('Product', models.DO_NOTHING, db_column='product_id')
    pro_attribute_id = models.ForeignKey('ProductAttribute', models.DO_NOTHING, db_column='pro_attribute_id')

    class Meta:
        managed = False
        db_table = 'category_product_attribute'
        unique_together = (('category_id', 'product_id', 'pro_attribute_id'),)


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    iso_code = models.CharField(max_length=7, blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'city'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Comment(models.Model):
    CONST_TYPE = "com"

    comment_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey('Post', models.DO_NOTHING, db_column='post_id', blank=True, null=True)
    parent_id = models.ForeignKey('self', models.DO_NOTHING, db_column='parent_id', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner', null=True, blank=True)
    content = models.TextField(blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES2, default='published')
    status_reason = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comment'
        ordering = ['-date_add']

    def __unicode__(self):
        return self.post_id.title


class Contact(models.Model):
    contact_id = models.AutoField(primary_key=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=128)
    mobile = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    customer_service = models.SmallIntegerField(choices=SERVICE_CHOICES, default=1)
    status = models.PositiveIntegerField(blank=True, null=True, default=0)

    class Meta:
        managed = False
        db_table = 'contact'
        ordering = ['-customer_service']


class Csvc(models.Model):
    csvc_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=245, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    price_in_pack = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    available_date = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'csvc'


class CustomerMessage(models.Model):
    owner_message_id = models.AutoField(primary_key=True)
    owner_thread_id = models.ForeignKey('CustomerThread', models.DO_NOTHING, db_column='owner_thread_id')
    user_id = models.PositiveIntegerField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    user_agent = models.CharField(max_length=128, blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'customer_message'


class CustomerThread(models.Model):
    owner_thread_id = models.AutoField(primary_key=True)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    order_id = models.ForeignKey('Order', models.DO_NOTHING, db_column='order_id', blank=True, null=True)
    status = models.CharField(max_length=8)
    email = models.CharField(max_length=128)
    token = models.CharField(max_length=12, blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'customer_thread'


class Customization(models.Model):
    customization_id = models.OneToOneField('CustomizedData', models.DO_NOTHING, db_column='customization_id',
                                            primary_key=True)
    cart_id = models.ForeignKey(Cart, models.DO_NOTHING, db_column='cart_id')
    product_id = models.ForeignKey('Product', models.DO_NOTHING, db_column='product_id')
    pro_attribute_id = models.ForeignKey('ProductAttribute', models.DO_NOTHING, db_column='pro_attribute_id',
                                         blank=True, null=True)
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'customization'


class CustomizedData(models.Model):
    customization_id = models.PositiveIntegerField(primary_key=True)
    type = models.IntegerField()
    index = models.IntegerField()
    name = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'customized_data'
        unique_together = (('customization_id', 'type', 'index'),)


class District(models.Model):
    district_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    city_id = models.ForeignKey(City, models.DO_NOTHING, db_column='city_id')

    class Meta:
        managed = False
        db_table = 'district'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class EmailQueue(models.Model):
    email_queue_id = models.AutoField(primary_key=True)
    from_name = models.CharField(max_length=64, blank=True, null=True)
    from_email = models.CharField(max_length=128)
    to_email = models.CharField(max_length=128)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    max_attempts = models.PositiveIntegerField()
    attempts = models.PositiveIntegerField()
    success = models.IntegerField()
    status = models.IntegerField()
    date_published = models.DateTimeField(auto_now=True)
    last_attempt = models.DateTimeField(auto_now=True)
    date_sent = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'email_queue'


class Feature(models.Model):
    feature_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    position = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'feature'

    objects = models.Manager()  # The default manager.

    def save(self, *args, **kwargs):
        super(Feature, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:fea_detail',
                       args=[self.pk])


class FeatureProduct(models.Model):
    auto_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey('Product', models.DO_NOTHING, db_column='product_id')
    feature_id = models.ForeignKey('Feature', models.DO_NOTHING, db_column='feature_id')
    feature_value_id = models.ForeignKey('FeatureValue', models.DO_NOTHING, db_column='feature_value_id')

    # feature_value_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feature_product'
        unique_together = (('feature_id', 'product_id',),)

    # def clean(self):
    #     feature_value_id = self.cleaned_data.get('feature_value_id')
    #     if feature_value_id and not isinstance(feature_value_id, FeatureValue):
    #         raise ValidationError("feature_value_id are incorrect")

    objects = models.Manager()  # The default manager.

    def __init__(self, *args, **kwargs):
        super(FeatureProduct, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(FeatureProduct, self).save(*args, **kwargs)

    #
    # def __str__(self):
    #     return self.product_id.name + self.feature_id.name + self.feature_value_id.value
    #
    # def __unicode__(self):
    #     return self.product_id.name + self.feature_id.name + self.feature_value_id.value

    def get_absolute_url(self):
        return reverse('main:feapro_detail',
                       args=[self.pk])

    def __str__(self):
        return self.feature_id.name

    def __unicode__(self):
        return self.feature_id.name


class FeatureValue(models.Model):
    feature_value_id = models.AutoField(primary_key=True)
    feature_id = models.ForeignKey('Feature', models.DO_NOTHING, db_column='feature_id')
    custom = models.PositiveIntegerField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'feature_value'

    objects = models.Manager()  # The default manager.

    def save(self, *args, **kwargs):
        super(FeatureValue, self).save(*args, **kwargs)

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value

    def get_absolute_url(self):
        return reverse('main:feaval_detail',
                       args=[self.pk])


class Lookup(models.Model):
    lookup_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    position = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'lookup'
        unique_together = (('name', 'type'),)

    objects = models.Manager()  # The default manager.

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super(Lookup, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:look_detail',
                       args=[self.pk])


class Manufacturer(models.Model):
    CONST_TYPE = "man"
    manufacturer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    active = models.SmallIntegerField(choices=ACTIVE_CHOICES, default=1)
    description_short = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=128)

    class Meta:
        managed = False
        db_table = 'manufacturer'

    objects = models.Manager()  # The default manager.

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) <= 30:
            self.slug = slugify(self.name)
        super(Manufacturer, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:manu_detail',
                       args=[self.pk])


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey('Order', models.DO_NOTHING, db_column='order_id')
    owner_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField()
    private = models.PositiveIntegerField()
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'message'


class MessageReaded(models.Model):
    message_id = models.OneToOneField(Message, models.DO_NOTHING, db_column='message_id', primary_key=True)
    user_id = models.PositiveIntegerField()
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'message_readed'
        unique_together = (('message_id', 'user_id'),)


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, models.DO_NOTHING, db_column='owner_id')
    address_delivery = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='delivery', null=True,
                                         blank=True)
    address_invoice = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='invoice', null=True,
                                        blank=True)
    current_state = models.ForeignKey('OrderState', models.DO_NOTHING, db_column='current_state')
    valid = models.SmallIntegerField(default=0)
    secure_key = models.CharField(max_length=32)
    payment = models.CharField(max_length=255, blank=True, null=True)
    total_paid = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    total_wrapping = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    total_paid_real = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    invoice_date = models.DateTimeField(auto_now=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    cart_id = models.ForeignKey(Cart, models.DO_NOTHING, db_column='cart_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order'
        ordering = ['-date_add']


class OrderHistory(models.Model):
    order_history_id = models.AutoField(primary_key=True)
    user_id = models.PositiveIntegerField(blank=True, null=True)
    order_id = models.ForeignKey(Order, models.DO_NOTHING, db_column='order_id')
    order_state_id = models.ForeignKey('OrderState', models.DO_NOTHING, db_column='order_state_id')
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'order_history'


class OrderInvoice(models.Model):
    order_invoice_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order, models.DO_NOTHING, db_column='order_id')
    amount = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'order_invoice'


class OrderPayment(models.Model):
    CONST_TYPE = "pai"
    order_payment_id = models.AutoField(primary_key=True)
    order_reference = models.CharField(max_length=8, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.SmallIntegerField(choices=METHOD_PAYMENT_CHOICES, default=1)
    date_add = models.DateField(auto_now_add=True)
    data_payment = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_payment'
        ordering = ['-date_add']


class OrderInvoicePayment(models.Model):
    auto_id = models.AutoField(primary_key=True)
    order_invoice_id = models.ForeignKey(OrderInvoice, models.DO_NOTHING, db_column='order_invoice_id')
    order_payment_id = models.ForeignKey(OrderPayment, models.DO_NOTHING, db_column='order_payment_id')
    order_id = models.ForeignKey(Order, models.DO_NOTHING, db_column='order_id')
    sign = models.SmallIntegerField(choices=SIGN_CHOICES, default=0)

    class Meta:
        managed = False
        db_table = 'order_invoice_payment'
        unique_together = (('order_invoice_id', 'order_payment_id'),)
        ordering = ['-auto_id']


class OrderItem(models.Model):
    order_id = models.OneToOneField(Order, models.DO_NOTHING, db_column='order_id')
    find_item_id = models.CharField(max_length=128, primary_key=True)
    class_of_item = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unity = models.CharField(max_length=45, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    original_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_item'
        unique_together = (('order_id', 'find_item_id'),)
        ordering = ['-find_item_id']

    def save(self, *args, **kwargs):
        if to_python(self.class_of_item):
            try:
                _item = next(serializers.deserialize("json", self.class_of_item)).object
                if isinstance(_item, ProductAttribute):
                    self.price = _item.price
                    self.total_price = Decimal(_item.price) * self.quantity
            except:
                self.total_price = Decimal(self.price) * self.quantity
            finally:
                if almost_lt(self.total_price, 0.00, 2):
                    print("Something Wrong in save() CartItem {}".format(self.total_price))
        super(OrderItem, self).save(*args, **kwargs)


class OrderState(models.Model):
    order_state_id = models.AutoField(primary_key=True)
    invoice = models.PositiveIntegerField(blank=True, null=True)
    send_email = models.PositiveIntegerField()
    delivery = models.PositiveIntegerField()
    shipped = models.PositiveIntegerField()
    paid = models.PositiveIntegerField()
    deleted = models.PositiveIntegerField()
    name = models.CharField(max_length=128, blank=True, null=True)
    template = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'order_state'
        ordering = ['-name']


class Pack(models.Model):
    pack_id = models.AutoField(primary_key=True)
    pack_group_id = models.ForeignKey('PackGroup', models.DO_NOTHING, db_column='pack_group_id')
    find_item_id = models.CharField(max_length=45)
    class_of_item = models.CharField(max_length=45, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price_in_pack = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    original_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pack'


class PackGroup(models.Model):
    pack_group_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description_short = models.CharField(max_length=255, blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    total_paid_real = models.DecimalField(max_digits=17, decimal_places=2, blank=True, null=True)
    available_for_order = models.PositiveIntegerField()
    available_date = models.DateTimeField(auto_now=True)
    active = models.SmallIntegerField(choices=ACTIVE_CHOICES, default=0)

    class Meta:
        managed = False
        db_table = 'pack_group'


class Param(models.Model):
    param_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    label = models.CharField(max_length=64, blank=True, null=True)
    value = models.TextField()
    group = models.CharField(max_length=45, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=45, blank=True, null=True)
    index = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'param'


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='PUBLISHED')


class ChildManager(models.Manager):
    pass


class Post(models.Model):
    CONST_TYPE = "pst"

    post_id = models.AutoField(primary_key=True)
    # user_add_id = models.ForeignKey(User, models.DO_NOTHING, db_column='user_add_id')
    # user_upd_id = models.PositiveInteger, l.kioField(blank=True, null=True)
    user_add = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_add', null=True,
                                 blank=True)
    user_upd = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_upd', null=True,
                                 blank=True)
    category_id = models.ForeignKey('Category', models.DO_NOTHING, db_column='category_id')
    title = models.CharField(max_length=230)
    slug = models.SlugField(unique=True, max_length=255)
    content = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=230, blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES3, default='PUBLISHED')

    class Meta:
        managed = False
        db_table = 'post'
        ordering = ['-date_add']

    children = ChildManager()
    objects = models.Manager()  # The default manager.

    published = PublishedManager()  # Our custom manager.

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) <= 30:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
        try:
            obj = PostCategory.objects.get(post_id=self.post_id, category_id=self.category_id)
            obj.post_id = self
            obj.category_id = self.category_id
            obj.save()
        except PostCategory.DoesNotExist:
            new_values = {'post_id': self, 'category_id': self.category_id}
            obj = PostCategory(**new_values)
            obj.save()

    def delete(self, *args, **kwargs):
        super(Post, self).delete(*args, **kwargs)
        del_photo(None, self)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:post_detail',
                       args=[self.pk])

    def get_absolute_url_html(self):  # redirects to detail view of this post
        return reverse("main:post_detail", kwargs={"pk": self.pk})

    def get_shared_url(self):
        return reverse('main:post_share',
                       args=[self.pk])


class PostCategory(models.Model):
    auto_id = models.AutoField(primary_key=True)
    post_id = models.ForeignKey('Post', models.DO_NOTHING, db_column='post_id')
    category_id = models.ForeignKey('Category', models.DO_NOTHING, db_column='category_id')

    class Meta:
        managed = False
        db_table = 'post_category'
        unique_together = (('post_id', 'category_id'),)


class Category(models.Model):
    CONST_TYPE = "cat"
    category_id = models.AutoField(primary_key=True)
    parent_id = models.ForeignKey('self', models.DO_NOTHING, db_column='parent_id', blank=True, null=True)
    active = models.SmallIntegerField(choices=ACTIVE_CHOICES, default=1)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=255)
    products = models.ManyToManyField('Product', through='CategoryProduct', related_name='category_product')

    # posts = models.ManyToManyField('Post', through='PostCategory', through_fields=('category_id', 'post_id'), related_name='post_category')

    class Meta:
        managed = False
        db_table = 'category'
        ordering = ['-date_add']

    objects = models.Manager()  # The default manager.

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) <= 30:
            self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(Category, self).delete(*args, **kwargs)
        del_photo(None, self)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:category_detail',
                       args=[self.pk])

    def get_products(self):
        return self.products.all()


class Product(models.Model):
    CONST_TYPE = "pro"
    product_id = models.AutoField(primary_key=True)
    manufacturer_id = models.ForeignKey(Manufacturer, models.DO_NOTHING, db_column='manufacturer_id')
    category_default_id = models.ForeignKey(Category, models.DO_NOTHING, db_column='category_default_id')
    # category_default_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_default', null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=3)
    unity = models.CharField(max_length=45, )
    active = models.SmallIntegerField(choices=ACTIVE_CHOICES, default=1)
    condition = models.CharField(max_length=32, choices=COND_CHOICES, default='new')
    show_price = models.SmallIntegerField(choices=SHOW_CHOICES, default=1)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    description_short = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    config = models.TextField(blank=True, null=True)
    attributes = models.ManyToManyField(Attribute, through='ProductAttributeGroup',
                                        through_fields=('product_id', 'attribute_id'))
    categories = models.ManyToManyField('Category', through='CategoryProduct', related_name='category_product')

    def extra_fields_by_attributes(self):
        extra_inline_model = []
        try:
            if isinstance(self.config, str) and is_json(self.config):
                data = ast.literal_eval(to_python(self.config))
                if not isinstance(data, dict):
                    self.config = ""
                    self.save()
        except (ValueError, TypeError, IndexError):
            pass
        num_groups = ProductAttributeGroup.objects.filter(product_id=self.product_id).count()
        if num_groups > 0:
            extra_inline_model.append('ProductAttributeInline')

        num_feature = Feature.objects.all().count()
        if num_feature > 0:
            extra_inline_model.append('FeatureProductInline')
        return extra_inline_model

    class Meta:
        managed = False
        db_table = 'product'
        ordering = ['-date_add']

    objects = models.Manager()  # The default manager.

    def save(self, *args, **kwargs):
        if not self.slug or len(self.slug) <= 30:
            self.slug = slugify(self.name)
        if self.config:
            self.config = to_python(self.config)
        super(Product, self).save(*args, **kwargs)
        try:
            obj = CategoryProduct.objects.get(category_id=self.category_default_id, product_id=self.product_id)
            obj.product_id = self
            obj.category_id = self.category_default_id
            obj.position = 0
            obj.save()
        except CategoryProduct.DoesNotExist:
            new_values = {'product_id': self, 'category_id': self.category_default_id}
            obj = CategoryProduct(**new_values)
            obj.position = 0
            obj.save()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:pro_detail',
                       args=[self.pk])

    def get_pro_atts(self):
        return ProductAttribute.objects.filter(product_id=self.product_id)[:8]

    def reload_config(self):
        self.config = proccessConfig(self)
        self.save()

    def delete(self, *args, **kwargs):
        objs = ProductAttribute.objects.filter(product_id=self.pk)
        for obj in objs:
            del_photo(None, obj)
        super(Product, self).delete(*args, **kwargs)
        del_photo(None, self)


class ProductAttribute(models.Model):
    CONST_TYPE = "att"
    pro_attribute_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, models.DO_NOTHING, db_column='product_id')
    attr_name = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=3)
    quantity = models.IntegerField()
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    available_date = models.DateTimeField(auto_now=True)
    attributes = models.ManyToManyField(Attribute, through='ProductAttributeCombination',
                                        through_fields=('pro_attribute_id', 'attribute_id'))

    def _set_combination(self, value):
        print(value)

    def _get_combination(self):
        _attributes = self.productattributecombination_set.all()  # this gets all the child related objects
        str_value = ''
        for attribute in _attributes:
            str_value += "{}:{}, ".format(attribute.pk,
                                          attribute.name)  # here i am just getting one of the fields from the Activities model
        return str_value

    combination = property(_get_combination, _set_combination)

    class Meta:
        managed = False
        db_table = 'product_attribute'
        unique_together = (('product_id', 'attr_name', 'price', 'quantity'),)
        ordering = ['-date_add']

    objects = models.Manager()  # The default manager.

    def save(self, *args, **kwargs):
        if not self.attr_name or len(self.attr_name) <= 3:
            self.attr_name = "{} {}".format(self.product_id.name, generate_slug(8))
        if not self.price:
            self.price = self.product_id.price
        if not self.quantity:
            self.quantity = 0
        super(ProductAttribute, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        obj = self.product_id
        super(ProductAttribute, self).delete(*args, **kwargs)
        if obj is not None:
            obj.config = proccessConfig(obj)
            obj.save()
        del_photo(None, self)

    def __str__(self):
        return self.attr_name

    def __unicode__(self):
        return self.attr_name

    def get_absolute_url(self):
        return reverse('main:pro_attr_detail',
                       args=[self.pk])


class ProductAttributeGroup(models.Model):
    auto_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, models.DO_NOTHING, db_column='product_id')
    attr_group_id = models.ForeignKey(AttributeGroup, models.DO_NOTHING, db_column='attr_group_id')
    attribute_id = models.ForeignKey(Attribute, models.DO_NOTHING, db_column='attribute_id')

    class Meta:
        managed = False
        db_table = 'product_attribute_group'
        unique_together = (('attribute_id', 'product_id'),)

    def save(self, *args, **kwargs):
        if not self.attr_group_id and self.attribute_id is not None:
            self.attr_group_id = self.attribute_id.attr_group_id
        super(ProductAttributeGroup, self).save(*args, **kwargs)
        if self.product_id is not None:
            self.product_id.config = proccessConfig(self.product_id)
            self.product_id.save()

    def delete(self, *args, **kwargs):
        obj = self.product_id
        super(ProductAttributeGroup, self).delete(*args, **kwargs)
        if obj is not None:
            obj.config = proccessConfig(obj)
            obj.save()
        del_photo(None, self)


class ProductAttributeCombination(models.Model):
    auto_id = models.AutoField(primary_key=True)
    attribute_id = models.ForeignKey(Attribute, models.DO_NOTHING, db_column='attribute_id')
    pro_attribute_id = models.ForeignKey(ProductAttribute, models.DO_NOTHING, db_column='pro_attribute_id')

    class Meta:
        managed = False
        db_table = 'product_attribute_combination'
        unique_together = (('attribute_id', 'pro_attribute_id'),)

    objects = models.Manager()  # The default manager.

    def __str__(self):
        return self.attribute_id.name

    def __unicode__(self):
        return self.attribute_id.name


class ProductAttributeTag(models.Model):
    auto_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey('Product', models.DO_NOTHING, db_column='product_id')
    pro_attribute_id = models.ForeignKey('ProductAttribute', models.DO_NOTHING, db_column='pro_attribute_id')
    tag_id = models.ForeignKey('Tag', models.DO_NOTHING, db_column='tag_id')
    frequency = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'product_attribute_tag'
        unique_together = (('pro_attribute_id', 'tag_id'),)


class ProductTag(models.Model):
    auto_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, models.DO_NOTHING, db_column='product_id')
    tag_id = models.ForeignKey('Tag', models.DO_NOTHING, db_column='tag_id')

    class Meta:
        managed = False
        db_table = 'product_tag'
        unique_together = (('product_id', 'tag_id'),)


class ProductCategory(models.Model):
    auto_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, models.DO_NOTHING, db_column='product_id')
    category_id = models.ForeignKey(Category, models.DO_NOTHING, db_column='category_id')

    class Meta:
        managed = False
        db_table = 'product_category'
        unique_together = (('product_id', 'category_id'),)


class Room(models.Model):
    room_id = models.AutoField(primary_key=True)
    name_room = models.CharField(max_length=128, blank=True, null=True)
    name_creator = models.CharField(max_length=64, blank=True, null=True)
    info = models.CharField(max_length=256, blank=True, null=True)
    user_upd_id = models.PositiveIntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    status_reason = models.TextField(blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'room'


class Room4Chat(models.Model):
    room_id4chat = models.AutoField(primary_key=True)
    content = models.TextField()
    status = models.IntegerField(blank=True, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    date_upd = models.DateTimeField(auto_now=True)
    owner_id = models.PositiveIntegerField()
    identity_type = models.CharField(max_length=45, blank=True, null=True)
    identity_object = models.CharField(max_length=45, blank=True, null=True)
    room_id = models.ForeignKey(Room, models.DO_NOTHING, db_column='room_id')
    old_content = models.TextField(blank=True, null=True)
    status_reason = models.TextField(blank=True, null=True)
    media = models.CharField(max_length=128, blank=True, null=True)
    type = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'room4chat'


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    price_in_pack = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    available_date = models.DateTimeField(auto_now=True)
    unity = models.CharField(max_length=45, blank=True, null=True)
    during_time = models.IntegerField(blank=True, null=True)
    during_average = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'service'


class SpecificPrice(models.Model):
    specific_price_id = models.AutoField(primary_key=True)
    spec_pri_ru_id = models.ForeignKey('SpecificPriceRule', models.DO_NOTHING,
                                       db_column='spec_pri_ru_id', blank=True, null=True)
    cart_id = models.ForeignKey(Cart, models.DO_NOTHING, db_column='cart_id')
    price = models.DecimalField(max_digits=20, decimal_places=6)
    find_item_id = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'specific_price'


class SpecificPriceRule(models.Model):
    spec_pri_ru_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    secure_key = models.CharField(max_length=45)
    to = models.DateField(blank=True, null=True)
    from_field = models.DateField(db_column='from', blank=True,
                                  null=True)  # Field renamed because it was a Python reserved word.
    quantity = models.PositiveIntegerField(blank=True, null=True)
    remain_qty = models.PositiveIntegerField(blank=True, null=True)
    type_rule_id = models.ForeignKey('TypeRule', models.DO_NOTHING, db_column='type_rule_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'specific_price_rule'


class Subscriber(models.Model):
    email = models.CharField(primary_key=True, max_length=128)
    first_name = models.CharField(max_length=45, blank=True, null=True)
    last_name = models.CharField(max_length=45, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_join = models.DateField(blank=True, null=True)
    service = models.CharField(max_length=7, blank=True, null=True)
    limited = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subscriber'


class SubscriberPost(models.Model):
    email = models.OneToOneField(Subscriber, models.DO_NOTHING, db_column='email', primary_key=True)
    post_id = models.ForeignKey('Post', models.DO_NOTHING, db_column='post_id')
    status = models.IntegerField(blank=True, null=True)
    date_sent = models.DateField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subscriber_post'
        unique_together = (('email', 'post_id'),)


class SubscriberProductAttribute(models.Model):
    email = models.OneToOneField(Subscriber, models.DO_NOTHING, db_column='email', primary_key=True)
    product_id = models.ForeignKey(Product, models.DO_NOTHING, db_column='product_id')
    pro_attribute_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    date_sent = models.DateField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subscriber_product_attribute'
        unique_together = (('email', 'product_id'),)


class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    name_en = models.CharField(unique=True, max_length=45)
    frequency = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tag'


class TypeRule(models.Model):
    type_rule_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    add_to_item = models.CharField(max_length=7, blank=True, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    ratio = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'type_rule'


class Ward(models.Model):
    ward_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    district_id = models.ForeignKey(District, models.DO_NOTHING, db_column='district_id')

    class Meta:
        managed = False
        db_table = 'ward'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Profile(models.Model):
    # user_id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # address = models.OneToOneField(Address, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, null=True, blank=True)
    verified = models.PositiveSmallIntegerField(choices=VERIFY_CHOICES, null=True, blank=True)
    social_joined = models.CharField(max_length=255, null=True, blank=True)
    gender = models.PositiveIntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    couple_status = models.PositiveIntegerField(choices=MA_STATUS_CHOICES, null=True, blank=True)

    def __str__(self):  # __unicode__ for Python 2
        return self.user.username

    class Meta:
        managed = False
        db_table = 'profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
