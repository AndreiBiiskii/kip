from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from device.views import LoginUser, logout_user, ChangePassword
from .views import *

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
]