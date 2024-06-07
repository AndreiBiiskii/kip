from django.urls import path

from .views import device

urlpatterns = [
    path('devices/', device, name='devices')
]