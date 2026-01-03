from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib import messages
from django.db.models import Avg



@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True)

    # SEARCH
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    # CATEGORY FILTER
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)

    

    # STOCK FILTER
    if request.GET.get('in_stock'):
        products = products.filter(stock__gt=0)

    # SORTING
    sort = request.GET.get('sort')
    if sort == 'recent':
        products = products.order_by('-added_on')
    elif sort == 'price_low':
        products = products.order_by('-price')
    elif sort == 'price_high':
        products = products.order_by('price')
    elif sort == 'name':
        products = products.order_by('name')

    context = {
        'products': products,
        'query': query,
        'category': category,
    }

    return render(request, 'product_list.html', context)


    
    
@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id, is_active=True)

    # Increment view count
    product.view_count += 1
    product.save()

    # Handle question submission
    if request.method == "POST":
        question_form = ProductQuestionForm(request.POST)
        if question_form.is_valid():
            q = question_form.save(commit=False)
            q.product = product
            q.customer = request.user
            q.save()

            if product.farmer:
                Notification.objects.create(
                    user=product.farmer,
                    message=f"New question on {product.name}"
                )
            return redirect('product_detail', id=product.id)
    else:
        question_form = ProductQuestionForm()

    questions = product.questions.all().order_by('-created_at')

    # Reviews and average rating (optional)
    reviews = product.reviews.all() if hasattr(product, 'reviews') else []
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] if reviews else 0
    average_rating = round(average_rating, 1) if average_rating else 0

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'related_products': related_products,
        'question_form': question_form,
        'questions': questions,
    })


@login_required
def product_edit(request, id):
    if request.session.get("selected_role") != "farmer" and not request.user.is_superuser:
        return redirect("product_list")


@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()

            Notification.objects.create(
                user=request.user,
                message=f"Product '{product.name}' added successfully"
            )

            return redirect('farmer_product_list')
    else:
        form = ProductForm()

    return render(request, 'product_add.html', {'form': form})


@login_required
def product_edit(request, id):
    product = get_object_or_404(Product, id=id, farmer=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            Notification.objects.create(
                user=request.user,
                message=f"Product '{product.name}' updated"
            )

            return redirect('farmer_product_list')

    else:
        form = ProductForm(instance=product)

    return render(request, 'product_edit.html', {'form': form})

@login_required
def product_delete(request, id):
    product = get_object_or_404(Product, id=id, farmer=request.user)
    product_name = product.name
    product.delete()

    Notification.objects.create(
        user=request.user,
        message=f"Product '{product_name}' deleted"
    )

    return redirect('farmer_product_list')


@login_required
def farmer_product_list(request):
    products = Product.objects.filter(farmer=request.user).order_by('-added_on')

    return render(request, 'farmer_product_list.html', {
        'products': products
    })

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'notifications.html', {
        'notifications': notifications
    })
@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False)\
        .update(is_read=True)
    return redirect('notifications')

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(request, "Added to wishlist ")
    else:
        messages.info(request, "Already in your wishlist")

    return redirect('product_detail', id=product.id)

@login_required
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('product')

    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })

@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        id=item_id,
        user=request.user
    )
    wishlist_item.delete()
    messages.success(request, "Removed from wishlist")
    return redirect('wishlist')

