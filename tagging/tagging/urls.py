"""tagging URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from backend import vLogin
from backend import tagging
from backend import taggingbai

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'api/accounts/login',vLogin.login),
    path(r'api/accounts/register',vLogin.register),
    path(r'api/accounts/auth',vLogin.auth),
    path(r'api/tagging/next',tagging.next),
    path(r'api/tagging/result',tagging.result),
    #test
    # path(r'test/makedata',tagging.makedata),
    path(r'test/loaddata',tagging.loaddata),
    path(r'test/upload',taggingbai.rawdata),
    path(r'test/rec',tagging.recover),
    path(r'test/user',tagging.users),

        #bai
    path(r'api/tagging/readtext',taggingbai.readtext)

]
