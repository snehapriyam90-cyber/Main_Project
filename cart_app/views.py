from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products_app.models import *
from .models import *
from customer_app.models import *
from django.urls import reverse




@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.error(request, f"{product.name} is out of stock!")
        return redirect("product_detail", id=product.id)

    cart, _ = Cart.objects.get_or_create(customer=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': product.quantity}  # ⭐ KEY LINE
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += product.quantity
            cart_item.save()
        else:
            messages.warning(request, f"Only {product.stock} items available.")

    messages.success(request, f"{product.name} added to your cart!")
    return redirect("view_cart")


@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(customer=request.user)
    items = cart.items.all()
    total_price = cart.total_price() if items else 0

    return render(request, "cart.html", {
        "cart": cart,
        "items": items,
        "total_price": total_price
    })


# ---------------- UPDATE CART ITEM QUANTITY ----------------
@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__customer=request.user
    )

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))

        if quantity <= 0:
            cart_item.delete()
            messages.success(
                request,
                f"{cart_item.product.name} removed from cart."
            )
        else:
            if quantity > cart_item.product.stock:
                messages.warning(
                    request,
                    f"Only {cart_item.product.stock} available. Quantity adjusted."
                )
                quantity = cart_item.product.stock

            cart_item.quantity = quantity
            cart_item.save()

            messages.success(
                request,
                f"{cart_item.product.name} quantity updated."
            )

    return redirect("view_cart")


@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__customer=request.user   # ✅ FIXED
    )

    product_name = cart_item.product.name
    cart_item.delete()

    messages.success(request, f"{product_name} removed from cart.")
    return redirect("view_cart")


from decimal import Decimal



# Razorpay imports
import razorpay
from django.conf import settings

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def place_order(request):
    cart = get_object_or_404(Cart, customer=request.user)
    items = cart.items.all()

    if not items:
        messages.error(request, "Your cart is empty!")
        return redirect("product_list")

    subtotal = sum(item.subtotal() for item in items)
    delivery_charge = 50 if subtotal < 300 else 0
    cod_charge = 50

    if request.method == "POST":
        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        delivery_address = request.POST.get("delivery_address")
        payment_method = request.POST.get("payment_method")

        total_amount = subtotal + delivery_charge
        if payment_method == "cod":
            total_amount += cod_charge

        # 1️⃣ CREATE ORDER
        order = Order.objects.create(
            customer=request.user,
            full_name=full_name,
            phone=phone,
            email=email,
            address=delivery_address,
            payment_method=payment_method,
            total_amount=total_amount,
            status="pending",
            delivery_charge=delivery_charge,
            cod_charge=cod_charge if payment_method == "cod" else 0
        )

        farmers_notified = set()

        # 2️⃣ CREATE ORDER ITEMS + NOTIFY FARMERS
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price()
            )

            # Reduce stock
            product = item.product
            product.stock -= item.quantity
            product.save()

            farmer = product.farmer
            if farmer not in farmers_notified:
                Notification.objects.create(
                    user=farmer,
                    message=f"New order #{order.id} received. Status: Pending",
                    link=reverse("farmer_orders")
                )
                farmers_notified.add(farmer)

        # 3️⃣ CUSTOMER NOTIFICATION
        Notification.objects.create(
            user=request.user,
            message=f"Your order #{order.id} has been placed successfully. Total ₹{order.total_amount}"
        )

        # Clear cart
        items.delete()

        # 4️⃣ PAYMENT FLOW
        if payment_method == "cod":
            return redirect("order_success", order_id=order.id)
        else:
            razorpay_order = client.order.create({
                "amount": int(order.total_amount * 100),
                "currency": "INR",
                "payment_capture": "1"
            })
            order.razorpay_order_id = razorpay_order["id"]
            order.save()

            return render(request, "razorpay_payment.html", {
                "order": order,
                "razorpay_order": razorpay_order,
                "razorpay_key": settings.RAZORPAY_KEY_ID
            })

    return render(request, "checkout.html", {
        "cart": cart,
        "items": items,
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "cod_charge": cod_charge,
        "total_price": subtotal + delivery_charge
    })


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    items = order.order_items.select_related('product').all()

    for item in items:
        item.subtotal = item.price * item.quantity
        # Fetch review specific to this order
        item.review = item.product.reviews.filter(
            customer=request.user,
            order=order
        ).first()  # Returns None if not reviewed yet

    return render(request, "order_summary.html", {
        "order": order,
        "items": items
    })




@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    items = order.order_items.all()

    return render(request, "order_success.html", {
        "order": order,
        "items": items,
        "status_choices": Order.STATUS_CHOICES
    })

# ---------------- ORDER HISTORY ----------------
@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by("-created_at")
    return render(request, "order_history.html", {"orders": orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    items = order.order_items.all()

    return render(request, "order_detail.html", {
        "order": order,
        "items": items,
        "status_choices": Order.STATUS_CHOICES
    })


# ---------------- TRACK ORDER STATUS ----------------
@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, "track_order.html", {"order": order})



@login_required
def submit_review(request, product_id, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    product = get_object_or_404(Product, id=product_id)

    # Prevent review if order not delivered
    if order.status != "delivered":
        messages.error(request, "You can review only after delivery.")
        return redirect("order_summary", order_id=order.id)

    # Prevent duplicate review for this order
    if Review.objects.filter(product=product, customer=request.user, order=order).exists():
        messages.warning(request, "You already reviewed this product in this order.")
        return redirect("order_summary", order_id=order.id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not rating or not comment:
            messages.error(request, "Please provide both rating and comment.")
            return redirect("order_summary", order_id=order.id)

        Review.objects.create(
            product=product,
            customer=request.user,
            order=order,
            rating=int(rating),
            comment=comment
        )

        messages.success(request, "Thank you for your review!")
        return redirect("order_summary", order_id=order.id)
