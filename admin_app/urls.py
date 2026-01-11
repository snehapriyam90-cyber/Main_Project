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
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/orders/", views.admin_orders, name="admin_orders"),
    path("admin/orders/<int:order_id>/", views.admin_order_detail, name="admin_order_detail"),
    path('admin/orders/<int:order_id>/update/', views.admin_update_order_status, name='admin_update_order_status'),
    path('admin/orders/<int:order_id>/cancel/', views.admin_cancel_order, name='admin_cancel_order'),
    path('admin/notifications/', views.admin_notifications, name='admin_notifications'),
    path('admin/customers/', views.admin_customers, name='admin_customers'),
    path('admin/customers/<int:customer_id>/orders/', views.admin_customer_orders, name='admin_customer_orders'),
    path('admin/customers/<int:customer_id>/block/', views.admin_block_customer, name='admin_block_customer'),
    path('admin/customers/<int:customer_id>/unblock/', views.admin_unblock_customer, name='admin_unblock_customer'),
    path('admin/farmers/',views. admin_farmer_management, name='admin_farmer_management'),

    path('admin/farmer/approve/<int:farmer_id>/', views.admin_approve_farmer, name='admin_approve_farmer'),
    path('admin/farmer/reject/<int:farmer_id>/', views.admin_reject_farmer, name='admin_reject_farmer'),
    path('admin/farmer/block/<int:farmer_id>/', views.admin_block_farmer, name='admin_block_farmer'),
    path(
    'admin/farmer/<int:farmer_user_id>/products/',
    views.admin_farmer_products,
    name='admin_farmer_products'
    ),
    path(
    "admin/farmer/<int:farmer_id>/sales/",
    views.admin_farmer_sales,
    name="admin_farmer_sales"
    ),
    path("admin/products/", views.admin_product_management, name="admin_product_management"),
    path("admin/products/delete/<int:product_id>/", views.admin_delete_product, name="admin_delete_product"),
    path("admin/products/toggle/<int:product_id>/", views.admin_toggle_product_status, name="admin_toggle_product_status"),
    path('product/<int:product_id>/approve/', views.admin_approve_product, name='admin_approve_product'),
    path('product/<int:product_id>/reject/', views.admin_reject_product, name='admin_reject_product'),
    path("reviews/", views.admin_review_management, name="admin_review_management"),
    path("reviews/delete/<int:review_id>/", views.admin_delete_review, name="admin_delete_review"),
    path("sales-report/", views.admin_sales_report, name="admin_sales_report"),
    path('system-activity/', views.admin_system_activity, name='admin_system_activity'),








]
