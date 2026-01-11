from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products_app.models import *
from cart_app.models import *
from .models import *
from .forms import *
from django.db.models import Sum, F,Avg, Count
from products_app.models import *
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def get_farmer_total_sales(farmer):
    sales = OrderItem.objects.filter(
        product__farmer=farmer,
        order__status='Delivered'
    ).aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total']

    return sales or 0
def get_farmer_rating(farmer):
    data = Review.objects.filter(
        product__farmer=farmer
    ).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    return {
        "average": round(data['avg_rating'], 1) if data['avg_rating'] else 0,
        "count": data['total_reviews']
    }

@login_required
def farmer_dashboard(request):
    products = Product.objects.filter(farmer=request.user)

    orders = Order.objects.filter(
        order_items__product__farmer=request.user
    ).distinct()

    rating_data = get_farmer_rating(request.user)
    total_sales = get_farmer_total_sales(request.user)

    # 🔔 Unread notifications count
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    context = {
        "products": products,
        "orders": orders,
        "rating": rating_data["average"],
        "review_count": rating_data["count"],
        "total_sales": total_sales,
        "unread_count": unread_count,   # ✅ ADD THIS
    }

    return render(request, "farmer_dashboard.html", context)

@login_required
def farmer_profile(request):
    try:
        profile = FarmerProfile.objects.get(user=request.user)
    except FarmerProfile.DoesNotExist:
        profile = None

    if request.method == "POST":
        form = FarmerProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            farmer = form.save(commit=False)
            farmer.user = request.user
            farmer.save()

            messages.success(request, "✅ Profile saved successfully!")
            return redirect("farmer_profile")
        else:
            print(form.errors)
            messages.error(request, "❌ Please correct the errors below and try again.")

    else:
        form = FarmerProfileForm(instance=profile)

    return render(request, "farmer_profile.html", {"form": form})

@login_required
def farmer_questions(request):
    questions = ProductQuestion.objects.filter(
        product__farmer=request.user
    ).order_by('-created_at')

    unanswered_count = questions.filter(answer__isnull=True).count()

    if request.method == "POST":
        q_id = request.POST.get('question_id')
        answer = request.POST.get('answer')

        question = ProductQuestion.objects.get(
            id=q_id,
            product__farmer=request.user
        )
        question.answer = answer
        question.save()

        # ✅ Mark related notifications as read
        Notification.objects.create(
            user=question.customer,
            message=f"Farmer replied to your question on {question.product.name}",
            link=reverse('product_detail', args=[question.product.id])
        )


        return redirect('farmer_questions')

    return render(request, 'farmer_questions.html', {
        'questions': questions,
        'unanswered_count': unanswered_count
    })

@login_required
def farmer_orders(request):
    orders = Order.objects.filter(
        order_items__product__farmer=request.user
    ).distinct().order_by("-created_at")

    return render(request, "farmer_orders.html", {"orders": orders})


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    farmer_items = order.order_items.select_related("product").filter(
        product__farmer=request.user
    )

    farmer_subtotal = Decimal("0.00")

    for item in farmer_items:
        bundle_qty = Decimal(item.product.quantity)
        ordered_qty = Decimal(item.quantity)
        bundle_price = Decimal(item.price)

        if bundle_qty > 0:
            bundles = ordered_qty / bundle_qty
            item.subtotal = (bundles * bundle_price).quantize(Decimal("0.01"))
        else:
            item.subtotal = Decimal("0.00")

        farmer_subtotal += item.subtotal

    delivery_charge = Decimal(getattr(order, "delivery_charge", 0))
    cod_charge = Decimal("0.00")

    if order.payment_method == "cod":
        cod_charge = Decimal(getattr(order, "cod_charge", 0))

    farmer_total = farmer_subtotal + delivery_charge + cod_charge

    # ✅ FARMER STATUS REQUEST
    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in dict(Order.STATUS_CHOICES):
            farmer_items.update(status=new_status)

            # 🔥 CHANGE HERE
            order.farmer_status = new_status
            order.admin_approved = False
            order.save()

            # 🔔 Notify admin only
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    message=f"Farmer requested status '{new_status}' for Order #{order.id}"
                )

        return redirect("farmer_orders")

    return render(request, "update_order_status.html", {
        "order": order,
        "items": farmer_items,
        "status_choices": Order.STATUS_CHOICES,
        "farmer_subtotal": farmer_subtotal,
        "delivery_charge": delivery_charge,
        "cod_charge": cod_charge,
        "farmer_total": farmer_total
    })

@login_required
def submit_review(request, product_id, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    product = get_object_or_404(Product, id=product_id)

    # ✅ Prevent duplicate review FOR SAME ORDER ONLY
    if Review.objects.filter(
        product=product,
        customer=request.user,
        order=order
    ).exists():
        messages.warning(request, "You already rated this product for this order.")
        return redirect("order_summary", order_id=order.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        Review.objects.create(
            product=product,
            customer=request.user,
            order=order,          # ✅ VERY IMPORTANT
            rating=rating,
            comment=comment
        )

        messages.success(request, "Thank you for rating this product!")

    return redirect("order_summary", order_id=order.id)

@login_required
def farmer_reviews(request):
    # Fetch reviews only for products owned by this farmer
    reviews = Review.objects.filter(
        product__farmer=request.user
    ).select_related("product", "customer").order_by("-created_at")

    return render(request, "farmer_reviews.html", {
        "reviews": reviews
    })

from collections import defaultdict
from decimal import Decimal

@login_required
def farmer_sales(request):

    order_items = OrderItem.objects.select_related("product", "order").filter(
        product__farmer=request.user,
        order__status="delivered",
        order__admin_approved=True

    )

    total_orders = order_items.values("order").distinct().count()
    total_quantity = 0
    total_earnings = Decimal("0.00")

    product_sales = defaultdict(lambda: {"quantity": 0, "amount": Decimal("0.00")})

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

    # Convert defaultdict to regular dict for template
    product_sales = dict(product_sales)

    # Chart data
    product_labels = list(product_sales.keys())
    product_amounts = [float(v["amount"]) for v in product_sales.values()]

    return render(request, "farmer_sales.html", {
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "total_earnings": total_earnings,
        "product_sales": product_sales,
        "product_labels": product_labels,
        "product_amounts": product_amounts,
    })

@login_required
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect("customer_dashboard")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "password_change.html", {"form": form})
