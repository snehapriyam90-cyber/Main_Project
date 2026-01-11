"""
URL configuration for organic_store_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from . import views

urlpatterns = [
    path('register/', views.customer_register, name='customer_register'),
    path('login/', views.customer_login, name='customer_login'),

    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),

    path('profile/', views.customer_profile, name='customer_profile'),
    path('change-password/', views.change_password, name='customer_change_password'),

    path('customer_notifications/', views.customer_notifications, name='customer_notifications'),
    path('customer_mark_notifications_read/', views.customer_mark_notifications_read, name='customer_mark_notifications_read'),


]
