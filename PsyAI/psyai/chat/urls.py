# chat/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('chat/', views.chat_view, name='chat'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('upgrade/', views.upgrade_view, name='upgrade'),
]