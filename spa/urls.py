"""spa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView

from main import views
from main.views import SignUpView, signin, signout
from spa import settings

urlpatterns = [
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon.ico')),
    path('admin/', admin.site.urls),

    path('main/', include(("main.urls", 'main'), namespace="main")),
    path('main/', include('django.contrib.auth.urls')),

    path('cart/', include(("cart.urls", 'cart'), namespace="cart")),
    path('cart/', include('django.contrib.auth.urls')),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup.html/', signin, name='register'),

    # path('login/', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html', }, name='login'),
    # path('login.html/', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html', }, name='signin'),
    path('login/', signin, name='login'),
    path('login.html/', signin, name='signin'),

    path('logout/', signout, name='logout'),
    path('logout.html/', signout, name='signout'),


    path('', views.Dashboard.as_view(), name='home'),
    path('index.html', views.Dashboard.as_view(), name='index'),

    path('ajax_chained_view/', views.AjaxChainedView.as_view(), name='ajax_chained_view'),
    path('ajax_check_exist/', views.AjaxCheckView.as_view(), name='ajax_check_exist'),

    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('tags_input/', include('tags_input.urls', namespace='tags_input')),
    path('chaining/', include('smart_selects.urls')),
    # path("select2/", include("django_select2.urls")),
    path('maintenance-mode/', include('maintenance_mode.urls')),
    path('nested_admin/', include('nested_admin.urls')),
    path('captcha/', include('captcha.urls')),
    # path('accounts/', include('allauth.urls')),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('_nested_admin/', include('nested_admin.urls')),
]
if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "Spa Admin"
admin.site.site_title = "Spa Admin Portal"
admin.site.index_title = "Welcome to Spa Researcher Portal"

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
