"""Ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path

from ecommerce.api.v1.swagger import SwaggerSchemaView

urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('dj-admin/', admin.site.urls),
    path('api/v1/', include('ecommerce.api.v1.urls')),
]

if settings.DEBUG:
    from django.views.generic import RedirectView
    urlpatterns += [
        path('api/root/', SwaggerSchemaView.as_view()),
        path('', RedirectView.as_view(url='/api/root/', permanent=False))
    ]

    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
