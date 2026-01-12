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
    path('', views.home, name='home'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('terms_conditions/', views.terms_conditions, name='terms_conditions'),
    path('search/', views.global_search, name='global_search'),
    path('home_product_list', views.home_product_list, name='home_product_list'),
    path('home/', views.home, name='home'),



]
