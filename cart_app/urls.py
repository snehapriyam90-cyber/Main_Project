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
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart_update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('order_place/', views.place_order, name='place_order'),
    path('order/<int:order_id>/summary/', views.order_summary, name='order_summary'),
    path('orders/', views.order_history, name='order_history'),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),  # DETAIL page
    path('order/<int:order_id>/track/', views.track_order, name='track_order'),
    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),
    path(
        "submit-review/<int:product_id>/<int:order_id>/",
        views.submit_review,
        name="submit_review"
    ),
]
