"""Django URL Configuration

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
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from personal.views import (
    home_screen_view
)

from SocialSite.views import (
    register_view,
    login_view,
    logout_view,
    account_view,
    account_search_view,
    edit_account_view,
)
import debug_toolbar

admin.site.site_header = 'SocialSite Admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__', include(debug_toolbar.urls)),
    path('', home_screen_view, name='home'),
    path('account/<user_id>/', account_view, name='view'),
    path('account/<user_id>/edit/', edit_account_view, name='edit'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('search/', account_search_view, name='search'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


