from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('fruits', 'Fruits'),
        ('vegetables', 'Vegetables'),
    )

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    weight = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    added_on = models.DateTimeField(auto_now_add=True)
    discount_percent = models.PositiveIntegerField(blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)

    def discounted_price(self):
        if self.discount_percent:
            discount_amount = (self.discount_percent / Decimal('100')) * self.price
            return self.price - discount_amount
        return self.price

    def __str__(self):
        return self.name


# ✅ REVIEW MODEL (PER PRODUCT + PER ORDER)
class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    # ✅ STRING reference → NO circular import
    order = models.ForeignKey(
        "cart_app.Order",
        on_delete=models.CASCADE
    )

    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ✅ Allows same product to be reviewed again in another order
        unique_together = ('product', 'customer', 'order')

    def __str__(self):
        return f"{self.customer.username} - {self.product.name}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class ProductQuestion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} - {self.product.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
