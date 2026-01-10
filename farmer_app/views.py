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

    # ✅ Only this farmer’s products
    farmer_items = order.order_items.select_related("product").filter(
        product__farmer=request.user
    )

    farmer_subtotal = Decimal("0.00")

    # ✅ APPLY BUNDLE LOGIC
    for item in farmer_items:
        bundle_qty = Decimal(item.product.quantity)     # e.g. 5
        ordered_qty = Decimal(item.quantity)             # e.g. 10
        bundle_price = Decimal(item.price)               # e.g. 102

        if bundle_qty > 0:
            bundles = ordered_qty / bundle_qty
            item.subtotal = (bundles * bundle_price).quantize(Decimal("0.01"))
        else:
            item.subtotal = Decimal("0.00")

        farmer_subtotal += item.subtotal

    # ✅ DELIVERY + COD CHARGES (ONLY IF APPLICABLE)
    delivery_charge = Decimal(getattr(order, "delivery_charge", 0))
    cod_charge = Decimal("0.00")

    if order.payment_method == "cod":
        cod_charge = Decimal(getattr(order, "cod_charge", 0))

    farmer_total = farmer_subtotal + delivery_charge + cod_charge

    # ✅ UPDATE STATUS
    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in dict(Order.STATUS_CHOICES):
            farmer_items.update(status=new_status)


            Notification.objects.create(
                user=order.customer,
                message=f"Your order #{order.id} is now {new_status.capitalize()}."
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

