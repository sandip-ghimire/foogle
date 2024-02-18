"""
URL configuration for foogal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from .views import home, login, operations, config

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home.landing_page, name='home'),
    path('login', login.login_view, name='loginboard'),
    path('logout', auth_views.LogoutView.as_view(template_name='home.html'), name='logout'),
    path('upload', operations.handle_upload, name='upload'),
    path('config', config.config, name='config'),
    path('user_config', config.user_config, name='userconfig'),
    path('handle_settings', operations.handle_settings, name='handlesettings'),
    path('remove_files', operations.remove_files, name='removefiles'),
    path('links', operations.handle_links, name='links'),
    path('handle_asks', home.handle_asks, name='handleasks'),
    path('handle_local_links', home.handle_local_links, name='handlelocallinks')

]
