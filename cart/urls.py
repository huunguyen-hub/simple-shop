from django.urls import path

from . import views

urlpatterns = [
    path('add/<int:pk>/', views.cart_add, name='cart_add'),
    path('clear/<str:pk>/', views.cart_clear, name='cart_clear'),
    path('increment/<int:pk>/', views.cart_increment, name='cart_increment'),
    path('decrement/<int:pk>/', views.cart_decrement, name='cart_decrement'),
    path('reset/', views.cart_reset, name='cart_reset'),
    path('detail/', views.cart_detail, name='cart_detail'),
    path('update/', views.cart_update, name='cart_update'),
    path('process_<str:pk>.html/', views.cart_process, name='cart_process'),
    path('delivery_<str:pk>.html/', views.order_delivery, name='order_delivery'),
    path('invoice_<str:pk>.html/', views.order_invoice, name='order_invoice'),
    path('payment_<str:pk>.html/', views.order_payment, name='order_payment'),
    path('checkout_<str:pk>.html/', views.order_process, name='order_process'),
    path('online_<str:pk>_<str:name>.pdf', views.DisplayPDFView.as_view(), name='load_pdf'),
    path('online_<str:pk>_<str:name>.txt', views.txt_view, name='load_txt'),
]
