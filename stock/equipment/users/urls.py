from django.urls import path

from device.views import LoginUser, logout_user, ChangePassword

urlpatterns = [
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('change_password/', ChangePassword.as_view(), name='change_password'),
]
