"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from rest_framework import routers
from api.views import first, User, send_sms_code, verify_phone, CreateUser, reset_pass, reset_pass_verify, resetPass, CustomAuthToken
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()


urlpatterns = [
	path('', include(router.urls)),
    path('customauth/', CustomAuthToken.as_view()),
    path('auth/', obtain_auth_token),
	path('first/', first),
	path('me/', User.as_view()),
    path('createuser/', CreateUser.as_view()),
    path('send_sms_code/', send_sms_code),
    path('verify_phone/<int:sms_code>', verify_phone),
    path('reset/', reset_pass),
    path('reset_pass_verify/<int:reset_sms>', reset_pass_verify),
    path('reset-pass/', resetPass),
] 
