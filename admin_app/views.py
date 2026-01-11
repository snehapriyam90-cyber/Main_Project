from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from cart_app.models import *
from products_app.models import *
from farmer_app.models import *
from customer_app.models import *
import json
from decimal import Decimal


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):

    # ---------------- KPI CARDS ----------------
    delivered_items = OrderItem.objects.filter(
        order__status="delivered",
        order__admin_approved=True
    )
    order_items = OrderItem.objects.select_related('order', 'product', 'product__farmer').filter(
        order__status='delivered',
        order__admin_approved=True
    )

    total_revenue = Decimal("0.00")
    for item in delivered_items:
        if item.product.quantity > 0:
            total_revenue += (Decimal(item.quantity) / Decimal(item.product.quantity)) * Decimal(item.price)
    
    total_platform_revenue = Decimal('0.00')
    processed_orders = set()
    for item in order_items:
        bundle_qty = Decimal(item.product.quantity)
        ordered_qty = Decimal(item.quantity)
        price = Decimal(item.price)
        subtotal = (ordered_qty / bundle_qty * price) if bundle_qty > 0 else Decimal('0.00')
        total_platform_revenue += subtotal

        # Add delivery/COD charges only once per order
        if item.order.id not in processed_orders:
            total_platform_revenue += getattr(item.order, 'delivery_charge', 0)
            if item.order.payment_method == 'cod':
                total_platform_revenue += getattr(item.order, 'cod_charge', 0)
            processed_orders.add(item.order.id)

    total_orders = Order.objects.count()
    total_farmers = FarmerProfile.objects.filter(verified_farmer=True).count()
    total_customers = Profile.objects.count()
    total_products = Product.objects.filter(is_active=True).count()
    pending_farmers = FarmerProfile.objects.filter(verified_farmer=False).count()

    # ---------------- ORDER STATUS ----------------
    order_status = Order.objects.values("status").annotate(count=Count("id"))
    status_labels = [s["status"] for s in order_status]
    status_counts = [s["count"] for s in order_status]

    # ---------------- TOP PRODUCTS ----------------
    product_data = defaultdict(Decimal)
    for item in delivered_items:
        if item.product.quantity > 0:
                product_data[item.product.name] += (Decimal(item.quantity) / Decimal(item.product.quantity)) * item.price

    top_products = sorted(
        [{"name": k, "revenue": v} for k, v in product_data.items()],
        key=lambda x: x["revenue"],
        reverse=True
    )[:5]

    # ---------------- TOP FARMERS ----------------
    farmer_data = defaultdict(Decimal)
    for item in delivered_items:
        farmer_data[item.product.farmer.username] += item.price

    top_farmers = sorted(
        [{"name": k, "revenue": v} for k, v in farmer_data.items()],
        key=lambda x: x["revenue"],
        reverse=True
    )[:5]

    # ---------------- RECENT ACTIVITY ----------------
    recent_orders = Order.objects.order_by("-updated_at")[:5]
    recent_reviews = Review.objects.order_by("-id")[:5]

    context = {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "total_farmers": total_farmers,
        "total_customers": total_customers,
        "total_products": total_products,
        "pending_farmers": pending_farmers,
        'total_earnings': round(total_platform_revenue, 2),

        "status_labels_json": json.dumps(status_labels),
        "status_counts_json": json.dumps(status_counts),

        "top_products": top_products,
        "top_farmers": top_farmers,

        "recent_orders": recent_orders,
        "recent_reviews": recent_reviews,
    }

    return render(request, "admin_dashboard.html", context)

@login_required
@user_passes_test(is_admin)
def admin_orders(request):
    orders = Order.objects.all().order_by("-created_at")

    return render(request, "admin_orders.html", {
        "orders": orders
    })


@login_required
def admin_update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.admin_approved = True
            order.save()

            Notification.objects.create(
                user=order.customer,
                message=f"Your order #{order.id} is now {new_status.capitalize()}."
            )

    return redirect("admin_orders")

@login_required
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.order_items.select_related('product', 'product__farmer').all()

    if request.method == "POST":
        for item in items:
            new_status = request.POST.get(f'status_{item.id}')
            if new_status and new_status in dict(Order.STATUS_CHOICES):
                old_status = item.status
                item.status = new_status
                item.save()

                # 🔔 Create notification for customer about this item update
                Notification.objects.create(
                    user=order.customer,
                    message=f"Order #{order.id}: Item '{item.product.name}' status updated from '{old_status.title()}' to '{new_status.title()}'."
                )

        # Update overall order status based on items
        if all(i.status == 'delivered' for i in items):
            order.status = 'delivered'
        elif any(i.status == 'cancelled' for i in items):
            order.status = 'processing'  # adjust logic if needed
        else:
            order.status = 'processing'
        order.save()

        # 🔔 Optional: notify farmers their items were processed by admin
        farmers = set(i.product.farmer for i in items)
        for farmer in farmers:
            Notification.objects.create(
                user=farmer,
                message=f"Admin has finalized the status of your items in Order #{order.id}."
            )

        return redirect('admin_order_detail', order_id=order.id)

    return render(request, 'admin_order_detail.html', {
        'order': order,
        'items': items,
        'status_choices': Order.STATUS_CHOICES
    })


@login_required
@user_passes_test(is_admin)
def admin_cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "cancelled"
    order.admin_approved = True
    order.save()

    Notification.objects.create(
        user=order.customer,
        message=f"Your order #{order.id} has been cancelled."
    )

    return redirect("admin_orders")

@login_required
@user_passes_test(is_admin)
def admin_notifications(request):

    # Fetch notifications for all admins
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "admin_notifications.html", {
        "notifications": notifications
    })

@login_required
@user_passes_test(lambda u: u.is_staff)  # only admin can access
def admin_customers(request):
    # Fetch only users who are NOT staff AND not farmers
    customers = User.objects.filter(is_staff=False).exclude(
        id__in=FarmerProfile.objects.values_list('user_id', flat=True)
    ).order_by('username')

    customer_list = []

    for user in customers:
        profile = Profile.objects.filter(user=user).first()
        address = Address.objects.filter(user=user, is_default=True).first()
        total_orders = Order.objects.filter(customer=user).count()

        customer_list.append({
            "user": user,
            "profile": profile,
            "address": address,
            "total_orders": total_orders,
            "is_active": user.is_active,
        })

    return render(request, "admin_customers.html", {"customers": customer_list})

@login_required
@user_passes_test(is_admin)
def admin_block_customer(request, customer_id):
    customer = get_object_or_404(User, id=customer_id, is_staff=False)
    customer.is_active = False
    customer.save()
    
    # Optional: Notify customer
    Notification.objects.create(
        user=customer,
        message="Your account has been blocked by admin."
    )

    return redirect("admin_customers")

@login_required
@user_passes_test(is_admin)
def admin_unblock_customer(request, customer_id):
    customer = get_object_or_404(User, id=customer_id, is_staff=False)
    customer.is_active = True
    customer.save()

    Notification.objects.create(
        user=customer,
        message="Your account has been unblocked by admin."
    )

    return redirect("admin_customers")
@login_required
@user_passes_test(is_admin)
def admin_customer_orders(request, customer_id):
    customer = get_object_or_404(User, id=customer_id, is_staff=False)
    orders = Order.objects.filter(customer=customer).order_by("-created_at")
    
    # Prefetch items for each order
    for order in orders:
        order.items = order.order_items.select_related('product').all()
    
    return render(request, "admin_customer_orders.html", {
        "customer": customer,
        "orders": orders
    })

@login_required
def admin_farmer_management(request):
    farmers = FarmerProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'admin_farmer_management.html', {'farmers': farmers})

@login_required
def admin_approve_farmer(request, farmer_id):
    farmer = FarmerProfile.objects.get(id=farmer_id)
    farmer.status = 'approved'
    farmer.verified_farmer = True
    farmer.payout_enabled = True
    farmer.save()
    return redirect('admin_farmer_management')

@login_required
def admin_reject_farmer(request, farmer_id):
    farmer = FarmerProfile.objects.get(id=farmer_id)
    farmer.status = 'rejected'
    farmer.verified_farmer = False
    farmer.save()
    return redirect('admin_farmer_management')

@login_required
def admin_block_farmer(request, farmer_id):
    farmer = FarmerProfile.objects.get(id=farmer_id)
    farmer.status = 'blocked'
    farmer.save()
    return redirect('admin_farmer_management')

@login_required
def admin_farmer_products(request, farmer_user_id):
    farmer = get_object_or_404(User, id=farmer_user_id)

    products = Product.objects.filter(
        farmer=farmer
    ).order_by("-added_on")

    return render(request, "admin_farmer_products.html", {
        "farmer": farmer,
        "products": products
    })

from decimal import Decimal
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User



@login_required
def admin_farmer_sales(request, farmer_id):

    farmer = get_object_or_404(User, id=farmer_id)

    order_items = OrderItem.objects.select_related(
        "product", "order"
    ).filter(
        product__farmer=farmer,
        order__status="delivered",
        order__admin_approved=True
    )

    total_orders = order_items.values("order").distinct().count()
    total_quantity = 0
    total_earnings = Decimal("0.00")

    product_sales = defaultdict(lambda: {
        "quantity": 0,
        "amount": Decimal("0.00")
    })

    for item in order_items:
        bundle_qty = Decimal(item.product.quantity)
        ordered_qty = Decimal(item.quantity)
        bundle_price = Decimal(item.price)

        if bundle_qty > 0:
            bundles = ordered_qty / bundle_qty
            subtotal = (bundles * bundle_price).quantize(Decimal("0.01"))
        else:
            subtotal = Decimal("0.00")

        total_quantity += int(ordered_qty)
        total_earnings += subtotal

        product_sales[item.product.name]["quantity"] += int(ordered_qty)
        product_sales[item.product.name]["amount"] += subtotal

    return render(request, "admin_farmer_sales.html", {
        "farmer": farmer,
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "total_earnings": total_earnings,
        "product_sales": dict(product_sales),
    })

@login_required
def admin_product_management(request):
    products = Product.objects.select_related("farmer").order_by("-added_on")

    return render(request, "admin_product_management.html", {
        "products": products
    })


@login_required
def admin_delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect("admin_product_management")


@login_required
def admin_toggle_product_status(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()
    return redirect("admin_product_management")

@login_required
@user_passes_test(is_admin)
def admin_approve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.admin_approved = True
    product.save()

    # Send notification to farmer
    Notification.objects.create(
        user=product.farmer,
        message=f"Your product '{product.name}' has been approved by admin."
    )

    return redirect(request.META.get('HTTP_REFERER', 'admin_product_management'))

@login_required
@user_passes_test(is_admin)
def admin_reject_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.admin_approved = False
    product.is_active = False  # Hide rejected product
    product.save()

    # Send notification to farmer
    Notification.objects.create(
        user=product.farmer,
        message=f"Your product '{product.name}' has been rejected by admin."
    )

    return redirect(request.META.get('HTTP_REFERER', 'admin_product_management'))

@login_required
@user_passes_test(is_admin)
def admin_review_management(request):
    reviews = Review.objects.select_related(
        "product",
        "customer",
        "order",
        "product__farmer"
    ).order_by("-created_at")

    return render(request, "admin_review_management.html", {
        "reviews": reviews
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect("admin_review_management")

from collections import defaultdict
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import render
from products_app.models import Product

@login_required
@user_passes_test(is_admin)
def admin_sales_report(request):
    # Only delivered & admin-approved order items
    order_items = OrderItem.objects.select_related('order', 'product', 'product__farmer').filter(
        order__status='delivered',
        order__admin_approved=True
    )

    # -------------------------------
    # TOTAL SUMMARY
    # -------------------------------
    total_orders = order_items.values('order').distinct().count()
    total_quantity = sum(item.quantity for item in order_items)

    # Platform revenue: sum of product sales + delivery + COD charges per order (count each order once)
    total_platform_revenue = Decimal('0.00')
    processed_orders = set()
    for item in order_items:
        bundle_qty = Decimal(item.product.quantity)
        ordered_qty = Decimal(item.quantity)
        price = Decimal(item.price)
        subtotal = (ordered_qty / bundle_qty * price) if bundle_qty > 0 else Decimal('0.00')
        total_platform_revenue += subtotal

        # Add delivery/COD charges only once per order
        if item.order.id not in processed_orders:
            total_platform_revenue += getattr(item.order, 'delivery_charge', 0)
            if item.order.payment_method == 'cod':
                total_platform_revenue += getattr(item.order, 'cod_charge', 0)
            processed_orders.add(item.order.id)

    # -------------------------------
    # ORDER STATUS DATA
    # -------------------------------
    status_data = Order.objects.values('status').annotate(count=Count('id'))
    status_labels = [s['status'].capitalize() for s in status_data]
    status_counts = [s['count'] for s in status_data]

    # -------------------------------
    # TOP PRODUCT SALES
    # -------------------------------
    product_data = defaultdict(lambda: {'quantity': 0, 'revenue': Decimal('0.00')})
    for item in order_items:
        product_name = item.product.name
        bundle_qty = Decimal(item.product.quantity)
        ordered_qty = Decimal(item.quantity)
        price = Decimal(item.price)
        revenue = (ordered_qty / bundle_qty * price) if bundle_qty > 0 else Decimal('0.00')

        product_data[product_name]['quantity'] += int(ordered_qty)
        product_data[product_name]['revenue'] += revenue

    # Convert to sorted list of top products by revenue
    top_products = sorted(
        [{'name': k, 'quantity': v['quantity'], 'revenue': v['revenue']} for k, v in product_data.items()],
        key=lambda x: x['revenue'],
        reverse=True
    )[:5]  # Top 5 products

    # -------------------------------
    # TOP FARMER EARNINGS
    # -------------------------------
    farmer_data = defaultdict(Decimal)
    for item in order_items:
        farmer = item.product.farmer.username
        bundle_qty = Decimal(item.product.quantity)
        ordered_qty = Decimal(item.quantity)
        price = Decimal(item.price)
        revenue = (ordered_qty / bundle_qty * price) if bundle_qty > 0 else Decimal('0.00')
        farmer_data[farmer] += revenue

    farmer_labels = list(farmer_data.keys())
    farmer_values = [float(farmer_data[f]) for f in farmer_labels]

    context = {
        'total_orders': total_orders,
        'total_quantity': total_quantity,
        'total_earnings': round(total_platform_revenue, 2),

        'status_labels': status_labels,
        'status_counts': status_counts,

        'top_products': top_products,  # Pass list for template table

        'farmer_labels': farmer_labels,
        'farmer_values': farmer_values,
    }

    return render(request, 'admin_sales_report.html', context)


from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.utils.timezone import now
from itertools import chain



def is_admin(user):
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_system_activity(request):

    activities = []

    # ----------------------------------
    # 1. NEW USER REGISTRATIONS
    # ----------------------------------
    users = User.objects.order_by('-date_joined')[:5]
    for u in users:
        activities.append({
            'type': 'registration',
            'description': f'New user registered: {u.username}',
            'time': u.date_joined
        })

    # ----------------------------------
    # 2. ORDER STATUS CHANGES
    # ----------------------------------
    orders = Order.objects.order_by('-id')[:5]
    for o in orders:
        activities.append({
            'type': 'order',
            'description': f'Order #{o.id} status changed to {o.status}',
            'time': o.updated_at if hasattr(o, 'updated_at') else now()
        })

    # ----------------------------------
    # 3. PRODUCT ADDED / UPDATED
    # (Product has `added_on`)
    # ----------------------------------
    products = Product.objects.order_by('-added_on')[:5]
    for p in products:
        activities.append({
            'type': 'product',
            'description': f'Product updated/added: {p.name}',
            'time': p.added_on
        })

    # ----------------------------------
    # 4. REVIEWS POSTED
    # (NO review.user → use product + rating)
    # ----------------------------------
    reviews = Review.objects.order_by('-id')[:5]
    for r in reviews:
        activities.append({
            'type': 'review',
            'description': f'New review for {r.product.name} (Rating: {r.rating})',
            'time': r.created_on if hasattr(r, 'created_on') else now()
        })

    # ----------------------------------
    # SORT ALL ACTIVITIES BY TIME
    # ----------------------------------
    activities = sorted(
        activities,
        key=lambda x: x['time'],
        reverse=True
    )

    context = {
        'activities': activities
    }

    return render(request, 'admin_system_activity.html', context)


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def admin_password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "admin_password_change.html", {"form": form})
