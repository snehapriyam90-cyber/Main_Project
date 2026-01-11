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
        path("farmer_dashboard/", views.farmer_dashboard, name="farmer_dashboard"),
        path("farmer_profile/", views.farmer_profile, name="farmer_profile"),
        path('farmer_questions/', views.farmer_questions, name='farmer_questions'),
        path("farmer_orders/", views.farmer_orders, name="farmer_orders"),
        path(
        "farmer_order/<int:order_id>/status/",
        views.update_order_status,
        name="update_order_status"
        ),
        path("farmer/reviews/", views.farmer_reviews, name="farmer_reviews"),
        path("farmer/sales/", views.farmer_sales, name="farmer_sales"),
        path('password-change/', views.password_change, name='farmer_change_password'),



]
