from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from farmer_app.models import *


from .forms import *
from .models import Profile
from cart_app.models import *
from products_app.models import *


def customer_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect("customer_login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    
    return render(request, "register.html", {"form": form})



# views.py
def customer_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        print("POST data:", request.POST)

        if form.is_valid():
            username_or_email = form.cleaned_data["username_or_email"]
            password = form.cleaned_data["password"]
            selected_role = form.cleaned_data.get("role")
            print("Selected role:", selected_role)   # debug

            user = None
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=username_or_email)
                except User.DoesNotExist:
                    user = None

            if user and user.check_password(password):
                login(request, user)

                if user.is_superuser:
                    return redirect("admin_dashboard")
                elif selected_role == "farmer":
                    return redirect("farmer_dashboard")
                elif selected_role == "customer":
                    return redirect("customer_dashboard")
            else:
                messages.error(request, "Invalid username/email or password")
        else:
            messages.error(request, "Please select a role")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})
                
  



@login_required
def customer_logout(request):
    request.session.flush()
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("customer_login")

@login_required
def customer_dashboard(request):
    user = request.user

    # 🔹 Cart Count
    cart = Cart.objects.filter(customer=user).first()
    cart_count = cart.items.count() if cart else 0

    # 🔹 Orders
    total_orders = Order.objects.filter(customer=user).count()
    active_orders = Order.objects.filter(
        customer=user
    ).exclude(status="Delivered").count()

    recent_orders = Order.objects.filter(customer=user).order_by("-created_at")[:5]

    # 🔹 Products
    recent_products = Product.objects.filter(
        is_active=True
    ).order_by("-added_on")[:4]

    # 🔹 Reviews
    review_count = Review.objects.filter(customer=user).count()

    # 🔹 Notifications
    unread_count = Notification.objects.filter(
        user=user,
        is_read=False
    ).count()

    context = {
        "cart_count": cart_count,
        "total_orders": total_orders,
        "active_orders": active_orders,
        "recent_orders": recent_orders,
        "recent_products": recent_products,
        "review_count": review_count,
        "unread_count": unread_count,  # ✅ added notifications
    }

    return render(request, "customer_dashboard.html", context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm, AddressForm
from .models import Profile, Address


@login_required
def customer_profile(request):
    user = request.user

    profile, _ = Profile.objects.get_or_create(user=user)
    address, _ = Address.objects.get_or_create(user=user, is_default=True)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        a_form = AddressForm(request.POST, instance=address)

        if u_form.is_valid() and p_form.is_valid() and a_form.is_valid():
            u_form.save()
            p_form.save()

            addr = a_form.save(commit=False)
            addr.user = user
            addr.is_default = True
            addr.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("customer_profile")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)
        a_form = AddressForm(instance=address)

    context = {
        "user_form": u_form,
        "profile_form": p_form,
        "address_form": a_form,
    }

    return render(request, "profile.html", context)

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully!")
            return redirect("customer_profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "change_password.html", {"form": form})

@login_required
def customer_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'customer_notifications.html', {'notifications': notifications})

@login_required
def customer_mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('customer_notifications')