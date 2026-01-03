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
    path('product_list', views.product_list, name='product_list'),
    path('product_detail/<int:id>', views.product_detail, name='product_detail'),
    path('product_add', views.product_add, name='product_add'),
    path('product_edit/<int:id>', views.product_edit, name='product_edit'),
    path('product_delete/<int:id>', views.product_delete, name='product_delete'),
    path('farmer_product_list/', views.farmer_product_list, name='farmer_product_list'),
    path('farmer_notifications/',views.notifications,name='notifications'),
    path('farmer_mark_notifications_read/',views.mark_notifications_read,name='mark_notifications_read'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('wishlist_add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist_remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),



]
