"""
Django settings for spa project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# PROJECT_DIR = os.path.dirname(__file__)
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'g^=edgzx)(*hxqfk-c34*(l_h=s$0lgp6f2rn%u&kt1s#8+ay%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.1.*', 'spa.vn']

# Application definition

INSTALLED_APPS = [
    'admin_interface',
    'colorfield',
    'extra_settings',
    'maintenance_mode',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',

    'django.contrib.humanize',
    'main.apps.MainConfig',
    'cart.apps.CartConfig',
    'django_prices',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'tags_input',
    'smart_selects',  # newer clever_selects
    'tabbed_admin',
    'nested_admin',
    'django_json_widget',
    'django_mysql',
    'django_better_admin_arrayfield',
    'django_select2',
    # 'rest_framework',
    # 'sorl.thumbnail',
    'debug_toolbar',
    'django_pdb',
    'crispy_forms',
    'fontawesome_5',
    'fa',
    # 'sanitizer',
    'captcha'
]

SITE_ID = 1
# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': '123',
            'secret': '456',
            'key': ''
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_pdb.middleware.PdbMiddleware',
    # 'spa.context_processors.GlobalRequestMiddleware',
]

ROOT_URLCONF = 'spa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processor.cart_total_amount',
                'maintenance_mode.context_processors.maintenance_mode',
                'spa.context_processors.basic_context_processor',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    # 'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'spa.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'spadb',
        'HOST': 'localhost',
        'PASSWORD': 'admin1978',
        'USER': 'root',
        'OPTIONS': {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            'charset': 'utf8mb4',
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# All settings common to all environments
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main/static'),
    # os.path.join(os.path.dirname(__file__), 'static').replace('\\', '/'),
]
if DEBUG:
    TEMPLATE_DEBUG = True
else:
    TEMPLATE_DEBUG = False
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    # 'loggers': {
    #     'django.request': {
    #         'handlers': ['console'],
    #         'propagate': False,
    #         'level': 'DEBUG',
    #     },
    # },
}
THUMBNAIL_ALIASES = {
    '': {
        'avatar': {'size': (50, 50), 'crop': True},
    },
}
CKEDITOR_JQUERY_URL = STATIC_URL + 'admin/js/vendor/jquery/jquery.js'
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_UPLOAD_PREFIX = MEDIA_URL + CKEDITOR_UPLOAD_PATH
# CKEDITOR_FILENAME_GENERATOR = 'ckeditor_uploader.utils.generate_uuid4_filename'
CKEDITOR_FILENAME_GENERATOR = 'spa.utils.generate_uuid4_filename'
# The user interface language localization to be used with CKEditor
CKEDITOR_UI_LANGUAGE_SELECTOR = 'spa.utils.get_ckeditor_language'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_THUMBNAIL_SIZE = (320, 240)
CKEDITOR_IMAGE_QUALITY = 40
CKEDITOR_BROWSE_SHOW_DIRS = True
# CKEDITOR_UPLOAD_SLUGIFY_FILENAME = False
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_RESTRICT_BY_DATE = False
CKEDITOR_RESTRICT_BY_USER = False
# AWS_QUERYSTRING_AUTH = False
# CKEDITOR_STORAGE_BACKEND = 'custom_storages/PublicMediaRootS3BotoStorage'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Default',
        'toolbar_Default': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak'],
            ['RemoveFormat', 'Source']
        ],
        "removePlugins": "stylesheetparser",
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'uploadwidget',
        ]),
    },
    'basic': {
        'toolbar': 'Basic', 'height': 150, 'width': '100%',
        'toolbar_Basic': [
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Subscript', 'Superscript', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', 'Outdent', 'Indent', 'Blockquote', '-', 'JustifyLeft',
                       'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table']},
            {'name': 'huunguyen', 'items': ['Preview', 'Maximize', 'RemoveFormat', 'Source']},
        ],
        "removePlugins": "stylesheetparser",
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'uploadwidget',
        ]),
    },
    'custom': {
        'toolbar': 'Custom', 'height': 200,
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ],
        "removePlugins": "stylesheetparser",
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'uploadwidget',
        ]),
    },
    'tiny': {
        'toolbar': 'Tiny', 'height': 100,
        'toolbar_Tiny': [
            ['Bold', 'Link', 'Unlink', 'Image'],
        ],
    },
    'special': {
        'toolbar': 'Special', 'height': 200,
        'toolbar_Special': [
            ['Bold'],
            ['CodeSnippet'],  # here
        ],
        'extraPlugins': 'codesnippet',  # here
    }
}
CMS_ENABLE_UPDATE_CHECK = False
CMS_UPDATE_CHECK_TYPE = 'patch'
# REST_FRAMEWORK = {
#     # Use Django's standard `django.contrib.auth` permissions,
#     # or allow read-only access for unauthenticated users.
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
#     ]
# }
TAGS_INPUT_MAPPINGS = {
    'spa.tags': {
        'field': 'tags',
    },
}
USE_DJANGO_JQUERY = True
CART_SESSION_ID = 'cart'
X_FRAME_OPTIONS = 'SAMEORIGIN'  # only if django version >= 3.0
TABBED_ADMIN_USE_JQUERY_UI = True
# if True the maintenance-mode will be activated
MAINTENANCE_MODE = None

# by default, to get/set the state value a local file backend is used
# if you want to use the db or cache, you can create a custom backend
# custom backends must extend 'maintenance_mode.backends.AbstractStateBackend' class
# and implement get_value(self) and set_value(self, val) methods
MAINTENANCE_MODE_STATE_BACKEND = 'maintenance_mode.backends.LocalFileBackend'

# by default, a file named "maintenance_mode_state.txt" will be created in the settings.py directory
# you can customize the state file path in case the default one is not writable
MAINTENANCE_MODE_STATE_FILE_PATH = 'maintenance_mode_state.txt'

# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = "select2"
# if True the template tag will fallback to django.conf.settings,
# very useful to retrieve conf settings such as DEBUG.
EXTRA_SETTINGS_FALLBACK_TO_CONF_SETTINGS = True

# the upload_to path value of settings of type 'file'
EXTRA_SETTINGS_FILE_UPLOAD_TO = 'files'

# the upload_to path value of settings of type 'image'
EXTRA_SETTINGS_IMAGE_UPLOAD_TO = 'images'

INTERNAL_IPS = [
    '192.168.1.1',
    '192.168.1.112',
    '127.0.0.1',
    '192.168.1.168'
]
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
TEST_MEMCACHE = False
if not DEBUG or TEST_MEMCACHE:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        },
        # … default cache config and others
        "_default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        },
        "select2": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/2",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
        "select2": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/2",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
CRISPY_TEMPLATE_PACK = "bootstrap4"
DJANGO_ICONS = {
    "ICONS": {
        "edit": {"name": "far fa-pencil"},
    },
}
