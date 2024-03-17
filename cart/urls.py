from django.urls import path
from .views import *

app_name = 'cart'

urlpatterns = [
    path('', cart_summary, name='cart_summary'),
    path('detail_cart/<int:pk>', detail_cart, name='detail_cart'),
    path('cart_add/', cart_add, name='cart_add'),
    path('cart_update/', cart_update, name='cart_update'),
    path('cart_delete/', cart_delete, name='cart_delete'),
    path('order_info/', order_info, name='order_info'),
    path('order_save/', order_details, name='order_save'),
]
