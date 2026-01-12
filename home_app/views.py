from django.shortcuts import render,get_object_or_404
from .models import *
from django.urls import reverse
from products_app.models import Product

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def blog_list(request):
    blogs_qs = Blog.objects.filter(is_published=True).order_by('-created_at')
    blog_count = blogs_qs.count()

    if blog_count >= 5:
        blogs = blogs_qs[:5]
    else:
        blogs = blogs_qs

    return render(request, 'blog_list.html', {
        'blogs': blogs,
        'blog_count': blog_count
    })

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, is_published=True)
    return render(request, 'blog_detail.html', {'blog': blog})

def contact(request):
    success = False

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        success = True

    return render(request, 'contact.html', {'success': success})

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def refund_policy(request):
    return render(request, 'refund_policy.html')

def terms_conditions(request):
    return render(request, 'terms_conditions.html')


def global_search(request):
    query = request.GET.get('q', '').lower()
    results = []

    if query:
        # ---- STATIC PAGES ----
        static_pages = [
            {'title': 'About Us', 'url': '/about/', 'keywords': ['about']},
            {'title': 'Contact', 'url': '/contact/', 'keywords': ['contact', 'help']},
            {'title': 'Privacy Policy', 'url': '/privacy-policy/', 'keywords': ['privacy']},
            {'title': 'Refund Policy', 'url': '/refund-policy/', 'keywords': ['refund', 'return']},
            {'title': 'Terms & Conditions', 'url': '/terms-conditions/', 'keywords': ['terms']},
            {'title': 'Blogs', 'url': '/blogs/', 'keywords': ['blog', 'blogs']},
        ]

        for page in static_pages:
            if any(word in query for word in page['keywords']):
                results.append({
                    'type': 'Page',
                    'title': page['title'],
                    'url': page['url']
                })

        # ---- PRODUCTS ----
        products = Product.objects.filter(
            name__icontains=query,
            is_active=True
        )

        for product in products:
            results.append({
                'type': 'Product',
                'title': product.name,
                'url': reverse('product_detail', args=[product.id])
            })
        blogs = Blog.objects.filter(
            is_published=True,
            title__icontains=query
        )

        for blog in blogs:
            results.append({
                'type': 'Blog',
                'title': blog.title,
                'url': reverse('blog_detail', args=[blog.slug])
            })

    return render(request, 'global_search.html', {
        'query': query,
        'results': results
    })

def home_product_list(request):
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

    return render(request, 'home_product_list.html', context)

def home(request):
    products = Product.objects.filter(is_active=True).order_by('-added_on')[:4]
    return render(request, 'index.html', {'products': products})


