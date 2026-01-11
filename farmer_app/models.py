from django.db import models
from django.contrib.auth.models import User

class FarmerProfile(models.Model):

    FARM_TYPE_CHOICES = (
        ('Organic', 'Organic'),
        ('Natural', 'Natural'),
        ('Mixed', 'Mixed'),
        ('Conventional', 'Conventional'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 👤 Personal Details
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()

    # 🌾 Farm Details
    farm_name = models.CharField(max_length=200)
    farm_type = models.CharField(max_length=20, choices=FARM_TYPE_CHOICES)
    years_of_experience = models.PositiveIntegerField()
    farm_description = models.TextField()


    STATE_CHOICES = [
    ("Andhra Pradesh", "Andhra Pradesh"),
    ("Arunachal Pradesh", "Arunachal Pradesh"),
    ("Assam", "Assam"),
    ("Bihar", "Bihar"),
    ("Chhattisgarh", "Chhattisgarh"),
    ("Goa", "Goa"),
    ("Gujarat", "Gujarat"),
    ("Haryana", "Haryana"),
    ("Himachal Pradesh", "Himachal Pradesh"),
    ("Jharkhand", "Jharkhand"),
    ("Karnataka", "Karnataka"),
    ("Kerala", "Kerala"),
    ("Madhya Pradesh", "Madhya Pradesh"),
    ("Maharashtra", "Maharashtra"),
    ("Manipur", "Manipur"),
    ("Meghalaya", "Meghalaya"),
    ("Mizoram", "Mizoram"),
    ("Nagaland", "Nagaland"),
    ("Odisha", "Odisha"),
    ("Punjab", "Punjab"),
    ("Rajasthan", "Rajasthan"),
    ("Sikkim", "Sikkim"),
    ("Tamil Nadu", "Tamil Nadu"),
    ("Telangana", "Telangana"),
    ("Tripura", "Tripura"),
    ("Uttar Pradesh", "Uttar Pradesh"),
    ("Uttarakhand", "Uttarakhand"),
    ("West Bengal", "West Bengal"),

    # Union Territories
    ("Andaman and Nicobar Islands", "Andaman and Nicobar Islands"),
    ("Chandigarh", "Chandigarh"),
    ("Dadra and Nagar Haveli and Daman and Diu", "Dadra and Nagar Haveli and Daman and Diu"),
    ("Delhi", "Delhi"),
    ("Jammu and Kashmir", "Jammu and Kashmir"),
    ("Ladakh", "Ladakh"),
    ("Lakshadweep", "Lakshadweep"),
    ("Puducherry", "Puducherry"),
]

    # 📍 Location Details
    address = models.TextField()
    state = models.CharField(max_length=100,choices=STATE_CHOICES)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # 🚚 Delivery & Operations
    delivers_to_home = models.BooleanField(default=True)
    delivery_radius_km = models.PositiveIntegerField(default=10)
    delivery_charges = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    # 🕒 Availability
    is_available = models.BooleanField(default=True)
    working_days = models.CharField(
        max_length=100,
        help_text="Example: Mon–Sat"
    )
    

    # ⭐ Trust & Verification
    government_registered = models.BooleanField(default=False)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    verified_farmer = models.BooleanField(default=False)

    STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('blocked', 'Blocked'),
    )

    status = models.CharField(
    max_length=20,
    choices=STATUS_CHOICES,
    default='pending'
    )


    # 📅 Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 🧾 Bank / Payout Details
    bank_account_holder = models.CharField(max_length=150)
    bank_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=15)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    payout_enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.farm_name
