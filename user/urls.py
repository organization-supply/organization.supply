from django.urls import path

from user import views

urlpatterns = [
    path('settings', views.settings, name='user_settings'),
]
