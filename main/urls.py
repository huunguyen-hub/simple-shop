from django.urls import path

from main import views_shop, views_post, views, views_service
from main.views import SignUpView, signin, signout

app_name = 'main'

urlpatterns = [
    path('', views_shop.ShopView.as_view(), name='shop_home'),
    path('shop.html', views_shop.ShopView.as_view(), name='shop'),
    path('products.html', views_shop.ProductView.as_view(), name='product_list'),
    path('pro_detail_<str:pk>.html', views_shop.ProductView.as_view(), name='pro_detail'),
    path('pro_attr_detail_<str:pk>.html', views_shop.ProductAtributeView.as_view(), name='pro_attr_detail'),
    path('attrs_detail_<str:pk>.html', views_shop.get_detail, name='attrs_detail'),

    path('posts.html', views_post.PostListView.as_view(), name='post_list'),
    path('post_<str:pk>.html', views_post.PostView.as_view(), name='post_detail'),
    path('post_<str:pk>/share.html', views_post.post_share, name='post_share'),

    path('contact.html', views.ContactView.as_view(), name='contact'),

    path('service.html', views_service.ServiceView.as_view(), name='service'),
]
