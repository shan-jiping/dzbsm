"""dzbsm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.views.static import serve
from users.views import IndexView
from action.views import list_platform
import xadmin


urlpatterns = [
    url('^$', IndexView.as_view(), name="index"),
    url(r'^xadmin/', xadmin.site.urls),
    url('^index$', IndexView.as_view(), name="index"),
    url(r'^captcha/', include('captcha.urls')),
    url(r"^users/", include('users.urls', namespace="users")),
    url(r"^action/", include('action.urls', namespace="action")),
    url('^list_platform', list_platform.as_view(), name="list_platform"),
]
