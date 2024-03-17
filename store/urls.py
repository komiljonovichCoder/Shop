from django.urls import path
from .views import *
from django.contrib.auth.views import PasswordChangeDoneView

urlpatterns = [
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', user_register, name='register'),
    path('detail/<int:pk>', detail, name='detail'),
    path('category/<int:pk>', category, name='category'),
    path('profile/', ProfileUserView.as_view(), name='profile'),
    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password-changed/', PasswordChangeDoneView.as_view(template_name='store/password_change_done.html'), name='password_change_done'),
]
