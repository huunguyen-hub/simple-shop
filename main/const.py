from django import forms

MAX_SIZE_IMAGES = 16
MAX_SIZE_PRO_IMAGES = 6
MAX_SIZE_UPLOADED = 4

SLIDER_TYPE_SWBH = {'thumbnail': [320, 240], 'big': [480, 640], 'sizes': 5}
SLIDER_TYPE_SHBW = {'thumbnail': [240, 320], 'big': [640, 480], 'sizes': 5}

IMG_EXT_WITH_DOT = {'.jpg', '.jpeg', '.png', '.gif'}
IMG_EXT_NO_DOT = {ext.replace('.', '') for ext in IMG_EXT_WITH_DOT}
# size big>small
IMG_SIZES_W = {(640, 480), (320, 240), (32, 24)}
IMG_SIZES_H = {(480, 640), (240, 320), (24, 32)}
IMAGE_SIZES = {*IMG_SIZES_W, *IMG_SIZES_H}

IMAGE_SIZES_W = {'big': (640, 480), 'mid': (320, 240), 'sm': (32, 24)}
IMAGE_SIZES_H = {'hbig': (480, 640), 'hmid': (240, 320), 'hsm': (24, 32)}
# IMAGE_SIZES_INDEX = {'big': (640, 480), 'mid': (320, 240), 'sm': (32, 24), 'hbig': (480, 640), 'hmid': (240, 320),
#                      'hsm': (24, 32)}
IMAGE_SIZES_INDEX = {**IMAGE_SIZES_W, **IMAGE_SIZES_H}

CONTENT_TYPES = {'application/pdf', 'image/jpg', 'image/jpeg', 'image/png', 'image/gif', 'text/plain',
                 'application/zip', 'application/rar', 'application/x-rar'}
IMGCON_TYPES = {'image/jpg', 'image/jpeg', 'image/png', 'image/gif'}
DOCCON_TYPES = {'application/pdf', 'text/plain', 'application/zip', 'application/rar', 'application/x-rar'}

MODE_SAVE_IMG_ZIP0 = 0  # save file1 and file2 -> file in pk folder file1, file2 is "H || W"
# from main.models import PublishedManager

METHOD_PAYMENT1 = 1  # Trực tiếp
METHOD_PAYMENT2 = 2  # Chuyển khoản
METHOD_PAYMENT3 = 3  # Ví điện tử

METHOD_PAYMENT_CHOICES = (
    (METHOD_PAYMENT1, 'Paid In Store'),
    (METHOD_PAYMENT2, 'Bank Transfer'),
    (METHOD_PAYMENT3, 'Digital Wallet')
)

SECRET_KEY_CRYPT = 'secret_key'
SERVICE1 = 1  # Cus care
SERVICE2 = 2  # Report Error
SERVICE3 = 3  # Complain Order | Cart

SERVICE_CHOICES = (
    (SERVICE1, 'Cus care'),
    (SERVICE2, 'Report Error'),
    (SERVICE3, 'Complain Order | Cart')
)

TYPE0 = 0
TYPE1 = 1
TYPE2 = 2
TYPE3 = 3
TYPE4 = 4
TYPE5 = 5

SIGN_CHOICES = (
    (TYPE0, 'InActive'),
    (TYPE1, 'Active'),
    (TYPE2, 'Confirmed'),
    (TYPE3, 'SIGNED')
)

GROUP_CHOICES = (
    ('select', 'Select'),
    ('radio', 'Radio'),
    ('color', 'Color')
)

REGISTER = 1
MEMBER = 2
STAFF = 3
MANAGER = 4
SUPERVISOR = 5

ROLE_CHOICES = (
    (REGISTER, 'Register'),
    (MEMBER, 'Member'),
    (STAFF, 'Staff'),
    (MANAGER, 'Manager'),
    (SUPERVISOR, 'Supervisor'),
)

GENDER_CHOICES = (
    (0, 'Man'),
    (1, 'Woman'),
    (2, 'Unsex'),
)

MA_STATUS_CHOICES = (
    (1, 'Single'),
    (2, 'Marriage'),
    (3, 'Divorce'),
    (4, 'Dig'),
)

VERIFY1 = 1  # email or mobile
VERIFY2 = 2  # social_google
VERIFY3 = 3  # social_facebook
VERIFY4 = 4  # social_twitter
VERIFY5 = 5  # social_zalo
VERIFY6 = 6  # social_linkedin
VERIFY7 = 7  # social_wechat
VERIFY8 = 8  # social_tiktok
VERIFY9 = 9  # social_hub
VERIFY10 = 10  # social_other
VERIFY0 = 0  # not verified

VERIFY_CHOICES = (
    (VERIFY0, 'InVerified'),
    (VERIFY1, 'Email or Mobile'),
    (VERIFY2, 'Google'),
    (VERIFY3, 'FaceBook'),
    (VERIFY4, 'Twitter'),
    (VERIFY5, 'Zalo'),
    (VERIFY6, 'Linkedin'),
    (VERIFY7, 'Wechat'),
    (VERIFY8, 'Tiktok'),
    (VERIFY9, 'Hub'),
    (VERIFY10, 'Social Other'),
)

STATUS_CHOICES = (
    (TYPE1, 'InActive'),
    (TYPE2, 'Active')
)

STATUS_CHOICES2 = (
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('deleted', 'Deleted'),
    ('pending', 'Pending'),
)
STATUS_CHOICES3 = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
    ('DELETED', 'Deleted'),
    ('PENDING', 'Pending'),
)
ACTIVE_CHOICES = (
    (TYPE1, 'InActive'),
    (TYPE2, 'Active')
)
COND_CHOICES = (
    ('new', 'New'),
    ('used', 'Used'),
    ('refurbished', 'Refurbished')
)
SHOW_CHOICES = (
    (TYPE1, 'InActive'),
    (TYPE2, 'Active')
)


class CombineByMeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "Combine By Me"


class AttributeGroupModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.public_name.title()


class AttributeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()


class ProductAttributeModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.attr_name.title()


class ProductModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()


class FeatureValueModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.value.title()


class FeatureModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()


class UnityModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()


class CatModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()


class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.email.capitalize()


class CityModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()


class DistrictModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()


class WardModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name.title()
